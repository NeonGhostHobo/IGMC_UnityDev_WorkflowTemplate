#!/usr/bin/env python3
"""Plan or apply the IGMC Codex-native repository scaffold."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from validators.validate_repository_contract import validate_schema


TEXT_SUFFIXES = {".md", ".txt", ".yml", ".yaml", ".json", ".py", ".toml"}


@dataclass(frozen=True)
class SourceFile:
    source: Path
    destination: Path
    component: str


@dataclass(frozen=True)
class Operation:
    path: str
    component: str
    action: str
    source_sha256: str
    destination_sha256: str | None


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def render_content(source: Path, values: dict[str, str]) -> bytes:
    content = source.read_bytes()
    if source.suffix.lower() not in TEXT_SUFFIXES:
        return content
    text = content.decode("utf-8")
    for key, value in values.items():
        token = "{{" + key + "}}"
        if source.suffix.lower() == ".json":
            text = text.replace(json.dumps(token), json.dumps(value))
        else:
            text = text.replace(token, value)
    return text.encode("utf-8")


def iter_bundle(root: Path, destination_root: Path, component: str) -> Iterable[SourceFile]:
    if not root.exists():
        raise SystemExit(f"Missing source bundle: {root}")
    for source in sorted(path for path in root.rglob("*") if path.is_file()):
        yield SourceFile(source, destination_root / source.relative_to(root), component)


def collect_sources(repo_root: Path, dest: Path, *, github_metadata: bool, github_ci: bool) -> list[SourceFile]:
    sources = list(iter_bundle(repo_root / "template", dest, "core"))
    sources.extend(
        [
            SourceFile(
                repo_root / "validators" / "validate_repository_contract.py",
                dest / "scripts" / "validate_repository_contract.py",
                "core-validator",
            ),
            SourceFile(
                repo_root / "standard" / "schemas" / "repository.schema.json",
                dest / ".igmc" / "schema" / "repository.schema.json",
                "core-schema",
            ),
        ]
    )
    if github_metadata or github_ci:
        sources.extend(iter_bundle(repo_root / "optional" / "github-metadata" / "template", dest, "github-metadata"))
    if github_ci:
        sources.extend(iter_bundle(repo_root / "optional" / "github-ci" / "template", dest, "github-ci"))
    destinations = [item.destination for item in sources]
    if len(destinations) != len(set(destinations)):
        raise SystemExit("Installer source bundles contain duplicate destination paths")
    return sources


def load_existing_contract(dest: Path) -> dict[str, object]:
    path = dest / ".igmc" / "repository.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read existing repository contract {path}: {exc}") from exc
    return data if isinstance(data, dict) else {}


def build_values(args: argparse.Namespace, repo_root: Path, dest: Path) -> dict[str, str]:
    existing = load_existing_contract(dest)
    repository = existing.get("repository", {}) if isinstance(existing.get("repository"), dict) else {}
    version = (repo_root / "standard" / "VERSION").read_text(encoding="utf-8").strip()
    return {
        "REPOSITORY_ID": args.repo_id or str(repository.get("id") or dest.name),
        "REPOSITORY_NAME": args.repo_name or str(repository.get("name") or dest.name),
        "REPOSITORY_ARCHETYPE": args.archetype or str(repository.get("archetype") or "generic-software"),
        "REPOSITORY_LIFECYCLE": args.lifecycle or str(repository.get("lifecycle") or "active"),
        "REPOSITORY_VISIBILITY": args.visibility or str(repository.get("visibility") or "private"),
        "IGMC_STANDARD_VERSION": version,
    }


def build_plan(sources: list[SourceFile], dest: Path, values: dict[str, str]) -> tuple[list[Operation], dict[Path, bytes]]:
    operations: list[Operation] = []
    rendered: dict[Path, bytes] = {}
    for item in sources:
        content = render_content(item.source, values)
        rendered[item.destination] = content
        source_hash = sha256_bytes(content)
        if not item.destination.exists():
            action = "create"
            destination_hash = None
        elif not item.destination.is_file():
            action = "conflict"
            destination_hash = None
        else:
            destination_hash = sha256_bytes(item.destination.read_bytes())
            action = "unchanged" if destination_hash == source_hash else "conflict"
        operations.append(
            Operation(
                path=item.destination.relative_to(dest).as_posix(),
                component=item.component,
                action=action,
                source_sha256=source_hash,
                destination_sha256=destination_hash,
            )
        )
    return operations, rendered


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def manifest_payload(
    *,
    dest: Path,
    values: dict[str, str],
    operations: list[Operation],
    mode: str,
    github_metadata: bool,
    github_ci: bool,
) -> dict[str, object]:
    return {
        "manifest_version": "2.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "repository": {
            "path": str(dest),
            "id": values["REPOSITORY_ID"],
            "archetype": values["REPOSITORY_ARCHETYPE"],
        },
        "standard_version": values["IGMC_STANDARD_VERSION"],
        "components": {
            "core": True,
            "github_metadata": github_metadata or github_ci,
            "github_ci": github_ci,
        },
        "operations": [asdict(operation) for operation in operations],
    }


def validate_choices(args: argparse.Namespace, repo_root: Path) -> None:
    archetypes = {path.stem for path in (repo_root / "standard" / "archetypes").glob("*.yml") if path.stem != "base"}
    if args.archetype and args.archetype not in archetypes:
        raise SystemExit(f"Unknown archetype {args.archetype!r}; choose one of: {', '.join(sorted(archetypes))}")
    if args.force and not args.apply:
        raise SystemExit("--force is valid only together with --apply")


def validate_rendered_contract(repo_root: Path, dest: Path, rendered: dict[Path, bytes]) -> None:
    contract_path = dest / ".igmc" / "repository.json"
    try:
        contract = json.loads(rendered[contract_path])
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Rendered repository contract is invalid JSON: {exc}") from exc
    schema = json.loads((repo_root / "standard" / "schemas" / "repository.schema.json").read_text(encoding="utf-8"))
    errors = validate_schema(contract, schema)
    if errors:
        raise SystemExit("Rendered repository contract is invalid:\n" + "\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan or apply the IGMC Codex-native scaffold.")
    parser.add_argument("--dest", default=".", help="Destination repository root")
    parser.add_argument("--apply", action="store_true", help="Apply the fully preflighted plan")
    parser.add_argument("--force", action="store_true", help="Explicitly overwrite conflicting managed files")
    parser.add_argument("--manifest", type=Path, help="Also write the generated plan manifest to this path")
    parser.add_argument("--repo-id")
    parser.add_argument("--repo-name")
    parser.add_argument("--archetype")
    parser.add_argument("--lifecycle", choices=("active", "maintenance", "archived"))
    parser.add_argument("--visibility", choices=("private", "internal", "public"))
    parser.add_argument("--with-github-metadata", action="store_true", help="Install optional issue and pull-request templates")
    parser.add_argument("--with-github-ci", action="store_true", help="Install optional deterministic validation CI; never runs AI")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    dest = Path(args.dest).resolve()
    validate_choices(args, repo_root)
    values = build_values(args, repo_root, dest)
    sources = collect_sources(
        repo_root,
        dest,
        github_metadata=args.with_github_metadata,
        github_ci=args.with_github_ci,
    )
    operations, rendered = build_plan(sources, dest, values)
    validate_rendered_contract(repo_root, dest, rendered)
    if args.apply and args.force:
        operations = [replace(operation, action="overwrite") if operation.action == "conflict" else operation for operation in operations]
    manifest = manifest_payload(
        dest=dest,
        values=values,
        operations=operations,
        mode="apply" if args.apply else "plan",
        github_metadata=args.with_github_metadata,
        github_ci=args.with_github_ci,
    )

    print(json.dumps(manifest, indent=2))
    if args.manifest:
        atomic_write(args.manifest.resolve(), (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))

    conflicts = [operation for operation in operations if operation.action == "conflict"]
    if not args.apply:
        print("Dry run only. Re-run with --apply after reviewing the plan.")
        return 2 if conflicts else 0
    if conflicts and not args.force:
        print("Refusing to apply because conflicts exist. Review the plan; use --force only for an intentional migration.")
        return 2

    for operation in operations:
        if operation.action == "unchanged":
            continue
        path = dest / operation.path
        atomic_write(path, rendered[path])

    audit_path = dest / ".igmc" / "migrations" / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}-scaffold.json"
    completed = dict(manifest)
    completed["state"] = "completed"
    atomic_write(audit_path, (json.dumps(completed, indent=2) + "\n").encode("utf-8"))
    print(f"Applied IGMC standard {values['IGMC_STANDARD_VERSION']} to {dest}")
    print(f"Audit manifest: {audit_path}")
    print("No remote task, scheduled job, paid model call, commit, push, or GitHub write was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
