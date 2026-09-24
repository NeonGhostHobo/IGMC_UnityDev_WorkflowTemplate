# Operating Standard v2 Implementation

## Delivered

- Codex-local-first standard and runtime policy.
- Compact `AGENTS.md` with explicit authority, cost, remote, and external-write boundaries.
- Four canonical skills for work, review, issues, and maintenance.
- Repository-specific Codex instructions for this workflow source.
- Strict JSON repository contract with an installed schema and dependency-free validator.
- Dry-run, preflighted, atomic installer with conflict blocking and audit manifests.
- Optional GitHub metadata and deterministic contract CI, excluded from the default scaffold.
- Managed-asset coverage validation and checksum verification.
- Installer and contract regression tests using temporary repositories.

## Intentionally removed from the core scaffold

- GitHub custom agents and Copilot-specific instructions.
- Scheduled nightly jobs.
- CI failure comment loops.
- Automatic rebases and force-pushes.
- Issue-triggered agent instructions.
- Mandatory reports and global review ledgers.
- Duplicate Markdown/JSON documentation artifacts.
- Unattended cross-repository scaffold pushes.

## Verification

Run:

```powershell
python validators/validate_standard_assets.py
python -m unittest discover -s tests -v
```

The test suite verifies dry-run behavior, explicit apply, metadata rendering, contract validation, conflict preflight, optional adapter boundaries, and managed-asset coverage.
