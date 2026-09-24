---
name: igmc-maintain
description: Validate or update an IGMC repository contract and Codex-native workflow installation. Use for alignment checks, scaffold upgrades, skill maintenance, or workflow migration.
---

# IGMC maintenance

1. Run `python scripts/validate_repository_contract.py .` and inspect `.igmc/repository.json`.
2. Compare the installed standard version and enabled skills with the requested workflow version.
3. For an upgrade, generate and review an installer plan before applying it. Never overwrite conflicts implicitly.
4. Keep repository-owned documentation and configuration unless an explicit migration names them.
5. Re-run contract validation plus the repository's declared local validation commands after changes.

Default to local execution. GitHub metadata and deterministic CI are optional adapters. Remote execution, schedules, external writes, and paid services require an explicit request.
