# Workflow Scaffold (IGMC)

This folder is the **single source of truth** for the IGMC repo workflow setup.

It is designed to be copyable into any repository (Unity or non-Unity) to make it compatible with:
- The IGMC Issue → Copilot → PR loop
- The PR + nightly **IGMC integrity gates**
- The CI failure → PolishingAgent loop (with attempt cap)
- The agent spec stack under `.github/agents/`

## Apply to another repo

From this repo root:

- `python3 workflow_scaffold/apply.py --dest /path/to/other-repo`

Options:
- Add `--force` to overwrite existing files.

## What gets installed

Everything under `workflow_scaffold/template/` is copied into the destination repo root, preserving paths:
- `.github/workflows/*`
- `.github/agents/*`
- `.github/copilot-instructions.md`
- `.github/ISSUE_TEMPLATE/igmc-intake.yml`
- `scripts/validate_artifacts.py`
- baseline `/docs/*` artifacts
- `tickets/` + `reports/` folders

## Notes

- The PR gate enforces that any non-doc changes also update required `/docs/*`, add/update at least one `tickets/*.md`, and add/update `review.md`.
- Unity compilation is intentionally **not** run in CI in this template.
