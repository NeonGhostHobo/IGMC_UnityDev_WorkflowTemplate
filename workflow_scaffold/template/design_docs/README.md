# Design Docs (IGMC Intake)

Drop a free-form design document here (Markdown recommended).

When a new file is pushed to `design_docs/`, the workflow `IGMC Design Doc Intake` will:
- create an Issue titled `IGMC: Design Doc Intake — <filename>`
- apply the `igmc` label
- include the document contents in the issue body

Intended flow:
1) Push a design doc into `design_docs/`
2) The workflow creates the intake Issue
3) Assign the Issue to Copilot coding agent
4) Copilot produces `tickets/*.md` (and required `docs/*`) in a PR
5) On merge, `IGMC Tickets → Issues` creates one IGMC Issue per new ticket

Notes:
- The scaffold does not hard-require any specific structure in the design doc.
- Keep docs reasonably sized; very large docs may be truncated in issue bodies.
