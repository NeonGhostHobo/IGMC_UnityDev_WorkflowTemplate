# Workflow Repository Source of Truth

The IGMC Workflow Repository owns the global Codex workflow standard. Installed repositories own their project-specific contract and documentation.

## Canonical sources

- `standard/repository-operating-standard.md`: human-readable policy.
- `standard/schemas/`: machine contracts.
- `standard/runtime/codex.yml`: model-role and cost boundaries.
- `standard/assets/managed-assets.json`: distributed and optional assets.
- `template/`: core Codex-native files.
- `optional/`: opt-in GitHub adapters.
- `validators/`: deterministic enforcement.
- `apply.py`: the only installer implementation.

Provider-specific generated files are adapters, not authorities. Repository files are never updated by an unattended cross-repository workflow. Upgrades begin with a local installer plan and require an explicit apply.
