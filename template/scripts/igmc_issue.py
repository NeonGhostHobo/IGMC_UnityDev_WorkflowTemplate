#!/usr/bin/env python3
"""Validate an IGMC issue draft and optionally publish it with GitHub CLI."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


REQUIRED_SECTIONS = ("Summary", "Acceptance criteria", "Validation", "Sources")
ISSUE_TYPES = {"bug", "feature", "maintenance", "documentation", "research"}


def fail(message: str) -> None:
    raise ValueError(message)


def read_draft(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    lines = text.splitlines()
    if not lines or not re.fullmatch(r"# IGMC: .+", lines[0]):
        fail("first line must be '# IGMC: <actionable title>'")
    title = lines[0][2:].strip()
    if len(title) > 256:
        fail("title exceeds GitHub's 256-character limit")

    metadata: dict[str, str] = {}
    for key in ("Schema version", "Type", "Area", "Status"):
        match = re.search(rf"^{key}:\s*(.+)$", text, flags=re.MULTILINE)
        if not match or not match.group(1).strip():
            fail(f"missing {key} metadata")
        metadata[key] = match.group(1).strip()
    if metadata["Schema version"] != "1.0":
        fail("schema version must be 1.0")
    if metadata["Type"] not in ISSUE_TYPES:
        fail(f"type must be one of: {', '.join(sorted(ISSUE_TYPES))}")
    if metadata["Status"] != "proposed":
        fail("new issue status must be proposed")

    headings = list(re.finditer(r"^## (.+)$", text, flags=re.MULTILINE))
    sections: dict[str, str] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[heading.group(1).strip()] = text[heading.end() : end].strip()
    for name in REQUIRED_SECTIONS:
        if not sections.get(name):
            fail(f"missing or empty '## {name}' section")
    if not re.search(r"^- \[ \] .+", sections["Acceptance criteria"], re.MULTILINE):
        fail("acceptance criteria need at least one unchecked checklist item")
    for name in ("Validation", "Sources"):
        if not re.search(r"^- .+", sections[name], re.MULTILINE):
            fail(f"'{name}' needs at least one list item")
    if re.search(r"\b(TODO|TBD|<placeholder>)\b", text, re.IGNORECASE):
        fail("draft contains an unfinished placeholder")
    return title, "\n".join(lines[1:]).strip() + "\n"


def gh(*args: str) -> str:
    result = subprocess.run(["gh", *args], text=True, capture_output=True, check=False)
    if result.returncode:
        fail(result.stderr.strip() or f"gh {' '.join(args)} failed")
    return result.stdout.strip()


def publish(title: str, body: str, repo: str | None) -> str:
    repo = repo or gh("repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner")
    existing = json.loads(
        gh("issue", "list", "--repo", repo, "--state", "all", "--limit", "1000", "--json", "title,url")
    )
    for issue in existing:
        if issue["title"].strip().casefold() == title.casefold():
            fail(f"issue title already exists: {issue['url']}")
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".md", delete=False) as temp:
        temp.write(body)
        body_path = Path(temp.name)
    try:
        return gh("issue", "create", "--repo", repo, "--title", title, "--body-file", str(body_path))
    finally:
        body_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "publish"))
    parser.add_argument("draft", type=Path)
    parser.add_argument("--repo", help="GitHub OWNER/REPO; defaults to current checkout")
    parser.add_argument(
        "--confirm-external-write",
        action="store_true",
        help="Required for publish; confirms that GitHub issue creation was explicitly requested",
    )
    args = parser.parse_args()
    try:
        title, body = read_draft(args.draft)
        if args.action == "check":
            print(f"Issue draft OK: {title}")
        else:
            if not args.confirm_external_write:
                fail("publish requires --confirm-external-write")
            print(publish(title, body, args.repo))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"IGMC issue error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
