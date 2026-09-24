# Workflow Scaffold Compatibility Wrapper

The canonical installer is `../apply.py`. This directory remains only for callers that still invoke `workflow_scaffold/apply.py`; the wrapper delegates to the root implementation.

The v2 installer is dry-run by default. Add `--apply` only after reviewing the generated plan. Optional GitHub metadata and deterministic CI require explicit flags. No remote task, scheduled AI, paid API call, commit, push, or publication is performed by the installer.
