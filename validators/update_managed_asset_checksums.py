#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ASSET_FILE = Path("standard/assets/managed-assets.json")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(path.read_bytes())
        return "sha256:" + digest.hexdigest()

    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        relative = child.relative_to(path).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(child.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def update_checksums(root: Path, *, write: bool) -> str:
    asset_path = root / ASSET_FILE
    registry = json.loads(asset_path.read_text(encoding="utf-8"))
    for asset in registry["assets"]:
        asset["checksum"] = sha256_path(root / asset["source"])
    updated = json.dumps(registry, indent=2) + "\n"
    if write:
        asset_path.write_text(updated, encoding="utf-8")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Update managed asset sha256 checksums.")
    parser.add_argument("--root", default=".", help="Workflow repository root")
    parser.add_argument("--write", action="store_true", help="Write updated checksums")
    args = parser.parse_args()

    updated = update_checksums(Path(args.root).resolve(), write=args.write)
    if not args.write:
        print(updated)
    else:
        print("Managed asset checksums updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
