# Copilot instructions (IGMC)

When you are assigned an Issue labeled `igmc` (or a PR titled `IGMC:`), follow this order strictly:

1) **Update required docs first (always)**
   - Create/update the following files so they reflect the Issue request and the current repo state:
     - `docs/context_pack.md`, `docs/context_pack.json`
     - `docs/goals.md`, `docs/goals.json`
     - `docs/design.md`, `docs/design.json`
     - `docs/plan.md`, `docs/plan.yaml`
   - Keep them deterministic, structured, and free of fluff.

2) **Generate tickets**
   - Create/update one or more `tickets/*.md` with clear purpose, dependencies, steps, files, definition of done, and evidence/tests.
   - Tickets must be executable without human decisions.

3) **Implement**
   - Implement the tickets with minimal, safe code changes.
   - Keep the Unity project compiling.

4) **Report**
   - Add/update a short report in `reports/YYYY-MM-DD.md` and `reports/YYYY-MM-DD.json` summarizing what was done.

CI repair loop:
- When CI fails, the workflow `IGMC CI Failure Loop` will post a comment on the PR with failing jobs/steps.
- Treat that comment as a PolishingAgent task: fix CI first with minimal changes.
- Each new failure will post a new "IGMC PolishingAgent task (attempt N)" comment; keep iterating until the PR gate is green.

CI gates to respect:
- PR gate runs the IGMC integrity checks and `scripts/validate_artifacts.py`.
- PR gate also requires that the `/docs/*` files (and at least one `tickets/*.md`) are updated whenever non-doc files change.
