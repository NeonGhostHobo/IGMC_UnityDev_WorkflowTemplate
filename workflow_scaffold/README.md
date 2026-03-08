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
- `.github/ISSUE_TEMPLATE/igmc-design-doc.yml`
- `.github/workflows/design_doc_intake.yml`
- `.github/workflows/tickets_to_issues.yml`
- `.github/workflows/igmc_pr_rebase.yml`
- `scripts/validate_artifacts.py`
- baseline `/docs/*` artifacts
- `tickets/` + `reports/` folders
- `design_docs/` folder

## Inputs supported

This scaffold supports two input styles:

### 1) Single Issue intake (existing)

- Create an Issue using `.github/ISSUE_TEMPLATE/igmc-intake.yml` (label `igmc`) or title it `IGMC: ...`
- Assign the Issue to Copilot coding agent
- Copilot opens a PR and iterates until CI passes

### 2) Design doc intake (new)

Two ways to provide a free-form design document:

- **Push a file** into `design_docs/` (Markdown recommended)
  - The workflow `IGMC Design Doc Intake` creates an Issue titled `IGMC: Design Doc Intake — <filename>` and labels it `igmc`.
- **Create an Issue** using `.github/ISSUE_TEMPLATE/igmc-design-doc.yml`

Intended flow:

1) Provide the design doc (file push or issue)
2) Assign the intake issue to Copilot coding agent
3) Copilot splits the doc into `tickets/*.md` (and updates required `/docs/*`) in a PR
4) After merge, `IGMC Tickets → Issues` creates one IGMC Issue per newly-added ticket

Notes:

- This scaffold automates issue creation from `design_docs/` and from new `tickets/*.md`.
- Depending on your GitHub/Copilot setup, you may still need to assign created issues to Copilot (the scaffold itself does not force assignment).

## Merge conflicts (parallel PRs)

There is no safe, general way to auto-resolve merge conflicts: Git cannot reliably infer intent when two PRs touch the same lines.

Recommended approach:

- Prefer **one PR at a time per feature area**.
- Use the design-doc intake to create a ticket set, then assign issues **in order** (dependency-first) to reduce overlapping edits.
- Keep tickets narrow and file-disjoint where possible (different scripts/shaders/scenes per ticket).

Automation fallback:

- If an IGMC PR is simply behind `main/master` (no true conflicts), comment `/igmc-rebase` on the PR.
  - The workflow `IGMC PR Rebase Helper` will attempt to rebase and force-push the PR branch (same-repo branches only).
  - If conflicts exist, it posts a comment and stops (manual/Copilot resolution still required).

## Notes

- The PR gate enforces that any non-doc changes also update required `/docs/*`, add/update at least one `tickets/*.md`, and add/update `review.md`.
- Unity compilation is intentionally **not** run in CI in this template.
