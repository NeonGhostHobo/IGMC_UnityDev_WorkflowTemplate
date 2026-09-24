# IGMC Workflow Repository

This repository is the source of truth for a Codex-native, local-first repository workflow.

The core distribution contains:

- a compact `AGENTS.md` authority and working contract;
- task-specific skills under `.agents/skills/`;
- a strict `.igmc/repository.json` contract and installed schema;
- deterministic local validators;
- canonical documentation directories;
- local issue drafting with optional, explicitly requested publication.

It does not install scheduled jobs, unattended AI, remote agents, GitHub automation, commits, pushes, or paid API calls.

## Apply to a repository

The installer is dry-run by default:

```powershell
python apply.py --dest F:\Repositories\Example --repo-id example --repo-name "Example" --archetype generic-software
```

Review the JSON plan, then apply it explicitly:

```powershell
python apply.py --dest F:\Repositories\Example --repo-id example --repo-name "Example" --archetype generic-software --apply
```

Existing differing files are reported as conflicts and block the complete apply. `--force` is available only with `--apply` and represents an explicit migration decision.

Optional GitHub surfaces are separate:

```powershell
# Issue and pull-request templates only
python apply.py --dest F:\Repositories\Example --with-github-metadata --apply

# Also add deterministic contract validation in GitHub Actions
python apply.py --dest F:\Repositories\Example --with-github-ci --apply
```

The optional CI workflow never invokes Codex or another AI service. GitHub-hosted runner usage may still be billable under the repository owner's GitHub plan, so it is never installed by default.

## Codex workflow

Open the destination repository in Codex and ask for the outcome. `AGENTS.md` establishes common boundaries, and Codex loads the relevant skill:

- `igmc-work` for implementation or fixes;
- `igmc-review` for review or diagnosis;
- `igmc-issues` for local issue drafting;
- `igmc-maintain` for contract validation or workflow upgrades.

Skills provide workflow knowledge. MCP servers are optional live-data or action providers. Connecting a tool never implies permission to publish, spend money, schedule work, or write to an external system.

## Source-of-truth layout

- `AGENTS.md`: source-repository boundaries and validation commands.
- `standard/`: operating standard, schemas, archetypes, policies, runtime profile, and managed assets.
- `template/`: the Codex-native core scaffold.
- `optional/`: explicitly selected integration adapters.
- `validators/`: deterministic validation code.
- `apply.py`: manifest-first installer.
- `workflow_scaffold/apply.py`: compatibility entrypoint that delegates to `apply.py`.

## Validate this repository

```powershell
python validators/validate_standard_assets.py
python -m unittest discover -s tests -v
```

Validate an installed repository:

```powershell
python scripts/validate_repository_contract.py .
```

## Design principles

- Local by default; remote and paid execution are explicit.
- Skills over duplicated provider-specific agent prompts.
- Deterministic contracts over prompt-enforced gates.
- Documentation updates when facts change, not on every source edit.
- Dry-run and manifests before repository-wide workflow changes.
- Git history for storage; GitHub automation only when it earns its maintenance and execution cost.
