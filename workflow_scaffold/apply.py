#!/usr/bin/env python3

import argparse
from pathlib import Path


def copy_tree(template_dir: Path, dest: Path, *, force: bool) -> None:
    for src in sorted(template_dir.rglob("*")):
        if src.is_dir():
            continue

        rel = src.relative_to(template_dir)
        dst = dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists() and not force:
            raise SystemExit(f"Refusing to overwrite existing file: {dst} (use --force)")

        dst.write_bytes(src.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply the IGMC workflow scaffold template into a repository."
    )
    parser.add_argument(
        "--dest",
        default=".",
        help="Destination repo root (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files",
    )

    args = parser.parse_args()
    dest = Path(args.dest).resolve()
    template_dir = Path(__file__).resolve().parent / "template"
    if not template_dir.exists():
        raise SystemExit(f"Missing template dir: {template_dir}")

    copy_tree(template_dir, dest, force=args.force)

    print("IGMC workflow scaffold applied")
    print(f"- Template: {template_dir}")
    print(f"- Dest: {dest}")
    print("Next: push changes, then create an Issue titled 'IGMC: ...' and assign to Copilot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
