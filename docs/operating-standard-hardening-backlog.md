# Operating Standard v2 Backlog

This file contains only unresolved work. Completed implementation belongs in `operating-standard-implementation.md` and Git history.

## Candidate follow-ups

### Command Deck adapter migration

- Read `.igmc/repository.json` v2.
- Treat Codex as the preferred interactive runtime through a provider-neutral interface.
- Remove assumptions that GitHub Copilot SDK is the workflow authority.
- Preserve normalized events and visible local/remote state.

This work belongs in the Command Deck repository, not here.

### Optional MCP integrations

Add an MCP integration only when a real live data source or controlled action is needed. Each integration must declare:

- read and write capabilities;
- authentication owner;
- data boundary;
- approval boundary;
- whether any operation can incur cost;
- behavior when disconnected.

Do not create an MCP server merely to wrap local filesystem or validation behavior that Codex already handles directly.

### Model evaluation fixtures

After representative task transcripts are available, add an opt-in eval pack for workload-role comparisons. It must never run on a schedule or as default CI. Store aggregate outcomes and configuration, not secrets or raw hidden reasoning.

### Optional GitHub Action maintenance

The optional example pins `actions/checkout` to a reviewed full commit SHA. Review and update that pin manually when opting into a newer action release; do not add automatic dependency-update workflows by default.
