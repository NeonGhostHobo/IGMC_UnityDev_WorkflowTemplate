# IGMC workflow source maintenance

This repository defines the IGMC Codex-native repository standard and its distribution. Do not apply the scaffold to this source repository as though it were a target project.

## Authority and scope

- For review or diagnosis, inspect and report without editing unless asked.
- For requested implementation, make scoped local changes and run proportionate local validation.
- Do not start remote tasks, schedules, paid model/API calls, commits, pushes, publication, or other external writes unless explicitly requested.
- Preserve unrelated work and keep optional integrations separate from the default core.

## Source boundaries

- `standard/` owns policy, schemas, archetypes, runtime guidance, and the managed-asset registry.
- `template/` owns files installed in every target repository.
- `optional/` owns explicitly selected adapters; GitHub surfaces do not belong in the default template.
- `apply.py` owns preflight, rendering, conflict handling, atomic writes, and audit manifests.
- `validators/` and `tests/` provide deterministic evidence.

When a managed source under `template/` or `optional/` changes, refresh checksums before validation:

```powershell
python validators/update_managed_asset_checksums.py --write
python validators/validate_standard_assets.py
python -m unittest discover -s tests -v
```
