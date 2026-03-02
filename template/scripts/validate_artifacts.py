import json
from pathlib import Path
import sys

REQUIRED_FILES = [
    "docs/context_pack.json",
    "docs/goals.json",
    "docs/design.json",
    "docs/plan.yaml",
]


def fail(msg: str):
    print(f"ARTIFACT VALIDATION FAIL: {msg}")
    sys.exit(1)


for f in REQUIRED_FILES:
    if not Path(f).exists():
        fail(f"Missing required file: {f}")

goals = json.loads(Path("docs/goals.json").read_text(encoding="utf-8"))
if "goals" not in goals or not goals["goals"]:
    fail("goals.json must contain non-empty 'goals' array")

context_pack = json.loads(Path("docs/context_pack.json").read_text(encoding="utf-8"))
required_cp_keys = ["scope", "non_goals", "constraints", "assumptions", "unknowns", "risks"]
for k in required_cp_keys:
    if k not in context_pack:
        fail(f"context_pack.json missing required key: {k}")

design = json.loads(Path("docs/design.json").read_text(encoding="utf-8"))
if "decisions" not in design or not isinstance(design["decisions"], list) or not design["decisions"]:
    fail("design.json must contain non-empty 'decisions' array")

# Ensure the Prime Directive exists as a goal
if not any(
    "nightly" in (g.get("title", "").lower())
    and ("integrity" in (g.get("title", "").lower()) or "gate" in (g.get("title", "").lower()))
    for g in goals["goals"]
):
    fail("goals.json must include a goal for nightly integrity gate")

print("Artifact validation OK")
