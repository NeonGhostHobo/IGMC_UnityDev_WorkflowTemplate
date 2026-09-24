#!/usr/bin/env python3
"""Validate the IGMC workflow-standard source and distribution inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from validate_repository_contract import validate_schema


REQUIRED_STANDARD_FILES = [
    "standard/VERSION",
    "standard/repository-operating-standard.md",
    "standard/runtime/codex.yml",
    "standard/schemas/repository.schema.json",
    "standard/schemas/migration-manifest.schema.json",
    "standard/schemas/alignment-rule.schema.json",
    "standard/schemas/issue.schema.json",
    "standard/schemas/managed-asset.schema.json",
    "standard/rules/quick.yml",
    "standard/policies/default-weights.yml",
    "standard/policies/critical-rules.yml",
    "standard/assets/managed-assets.json",
]

FORBIDDEN_PATHS = [
    ".github/workflows/apply_scaffold.yml",
    "workflow_scaffold/template",
    "template/.github/agents",
    "template/.github/workflows",
    "template/.github/copilot-instructions.md",
    "template/.igmc/repository.yml",
    "template/review.md",
    "template/reports",
]

REQUIRED_ARCHETYPES = {
    "generic-software",
    "rust-terminal-application",
    "unity-project",
    "web-application",
    "python-tool",
    "documentation-only",
    "javascript-library",
    "research-repository",
    "creative-prototype",
    "client-delivery",
}


def fail(message: str) -> None:
    print(f"STANDARD ASSET VALIDATION FAIL: {message}")
    raise SystemExit(1)


def require_file(root: Path, relative: str) -> Path:
    path = root / relative
    if not path.is_file():
        fail(f"Missing required file: {relative}")
    return path


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(path.read_bytes())
        return "sha256:" + digest.hexdigest()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        relative = child.relative_to(path).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(child.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def validate_json_schemas(root: Path) -> None:
    for path in (root / "standard" / "schemas").glob("*.json"):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"Invalid JSON schema {path.relative_to(root)}: {exc}")


def validate_contract_template(root: Path) -> None:
    template = require_file(root, "template/.igmc/repository.json").read_text(encoding="utf-8")
    values = {
        "REPOSITORY_ID": "validation-repo",
        "REPOSITORY_NAME": "Validation Repository",
        "REPOSITORY_ARCHETYPE": "generic-software",
        "REPOSITORY_LIFECYCLE": "active",
        "REPOSITORY_VISIBILITY": "private",
        "IGMC_STANDARD_VERSION": require_file(root, "standard/VERSION").read_text(encoding="utf-8").strip(),
    }
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    contract = json.loads(template)
    schema = json.loads(require_file(root, "standard/schemas/repository.schema.json").read_text(encoding="utf-8"))
    errors = validate_schema(contract, schema)
    if errors:
        fail("Contract template does not satisfy repository schema:\n" + "\n".join(errors))


def validate_archetypes(root: Path) -> None:
    archetype_dir = root / "standard" / "archetypes"
    found = {path.stem for path in archetype_dir.glob("*.yml") if path.stem != "base"}
    if found != REQUIRED_ARCHETYPES:
        fail(f"Archetype set mismatch; expected {sorted(REQUIRED_ARCHETYPES)}, got {sorted(found)}")
    for archetype in sorted(found):
        text = (archetype_dir / f"{archetype}.yml").read_text(encoding="utf-8")
        if re.search(rf"^id:\s*{re.escape(archetype)}\s*$", text, re.MULTILINE) is None:
            fail(f"Archetype {archetype} does not declare its filename as id")


def validate_managed_assets(root: Path) -> None:
    registry_path = require_file(root, "standard/assets/managed-assets.json")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    schema = json.loads(require_file(root, "standard/schemas/managed-asset.schema.json").read_text(encoding="utf-8"))
    errors = validate_schema(registry, schema)
    if errors:
        fail("Managed asset registry does not satisfy its schema:\n" + "\n".join(errors))
    assets = registry["assets"]
    if not assets:
        fail("Managed asset registry is empty")
    seen_ids: set[str] = set()
    for asset in assets:
        asset_id = asset["id"]
        if asset_id in seen_ids:
            fail(f"Duplicate managed asset id: {asset_id}")
        seen_ids.add(asset_id)
        source = root / asset["source"]
        if not source.exists():
            fail(f"Managed asset source does not exist: {asset['source']}")
        actual = sha256_path(source)
        if asset["checksum"] != actual:
            fail(f"Managed asset {asset_id} checksum mismatch: expected {asset['checksum']}, got {actual}")

    distributed_roots = [root / "template", root / "optional"]
    uncovered: list[str] = []
    asset_sources = [(root / asset["source"]).resolve() for asset in assets]
    for distributed_root in distributed_roots:
        for file in sorted(item for item in distributed_root.rglob("*") if item.is_file()):
            resolved = file.resolve()
            if not any(resolved == source or source in resolved.parents for source in asset_sources):
                uncovered.append(file.relative_to(root).as_posix())
    if uncovered:
        fail("Distributed files lack managed-asset coverage: " + ", ".join(uncovered))


def validate(root: Path) -> None:
    for relative in REQUIRED_STANDARD_FILES:
        require_file(root, relative)
    for relative in FORBIDDEN_PATHS:
        candidate = root / relative
        if candidate.is_file() or (candidate.is_dir() and any(candidate.rglob("*"))):
            fail(f"Forbidden legacy or default-automation path exists: {relative}")
    validate_json_schemas(root)
    validate_contract_template(root)
    validate_archetypes(root)
    validate_managed_assets(root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate IGMC workflow-standard source assets.")
    parser.add_argument("--root", default=".", help="Workflow repository root")
    args = parser.parse_args()
    validate(Path(args.root).resolve())
    print("Standard asset validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
