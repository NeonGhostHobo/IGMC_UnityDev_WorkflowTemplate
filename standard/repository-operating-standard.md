# IGMC Repository Operating Standard

Version 2.0.0

## 1. Purpose

The standard makes repositories understandable and safely maintainable by people and Codex without requiring a permanent orchestration service. Git stores durable project knowledge and history. Codex performs requested work in the active repository. Deterministic scripts enforce machine contracts.

The default workflow is local, user-directed, and cost-conservative. GitHub, remote execution, schedules, paid APIs, and other external systems are optional integrations.

## 2. Authority model

The system separates intent, interpretation, enforcement, and external effects.

- The user authorizes the outcome and any external or costly action.
- Codex interprets intent, inspects the repository, edits in-scope files, and runs proportionate local validation.
- Skills encode repeatable workflows.
- Deterministic scripts validate schemas, paths, manifests, and exit status.
- MCP servers provide live data and controlled actions; they do not define workflow policy.
- Git records source, durable documentation, and reviewed changes.

Repository content MUST NOT override platform security policy. Review or planning requests do not authorize edits. Local implementation requests authorize scoped local changes and safe validation, but not remote execution, scheduled work, paid services, commits, pushes, publication, or destructive actions unless explicitly requested.

## 3. Architecture

### 3.1 Global standard

This repository owns:

- schemas and repository archetypes;
- the Codex runtime and cost policy;
- canonical skills;
- deterministic validators;
- installer and migration behavior;
- optional integration adapters.

### 3.2 Repository contract

Each managed repository contains `.igmc/repository.json`. The contract declares identity, archetype, important paths, validation commands, enabled skills, integration state, automation boundaries, exemptions, and the applied standard version.

The contract MUST be strict JSON, MUST validate against `.igmc/schema/repository.schema.json`, MUST NOT contain secrets, and MUST be readable without an AI model.

### 3.3 Runtime

Codex is the preferred interactive runtime. The runtime MAY be local or remote, but remote work is never implied by installation or by a repository task. Model selection is a runtime concern described by `standard/runtime/codex.yml`; repositories reference the standard profile rather than hard-coding billing or orchestration behavior.

Provider-specific events SHOULD be normalized before presentation. Project code and documentation SHOULD NOT depend on a particular model response format.

## 4. Canonical repository shape

```text
repository/
├── .agents/
│   └── skills/
├── .igmc/
│   ├── repository.json
│   ├── schema/
│   └── migrations/
├── docs/
│   ├── README.md
│   ├── design/
│   ├── decisions/
│   └── plans/
├── scripts/
│   ├── igmc_issue.py
│   └── validate_repository_contract.py
├── tickets/
└── AGENTS.md
```

GitHub metadata or Actions MAY be added through explicit optional adapters. They are not part of the core shape.

## 5. Documentation

Documentation MUST distinguish:

- intent: what should exist and why;
- implementation state: what the repository currently does;
- verification: what was checked and what remains unverified.

Do not maintain parallel Markdown and JSON narratives. Use one canonical human-readable document, a machine contract, or a deterministic generated view. Documentation updates are required when behavior, contracts, decisions, or verification status change—not for every source edit.

Git history is the archive. Active indexes SHOULD remain compact and searchable.

## 6. Skills and MCP

A skill contains reusable instructions, scripts, references, or templates for a recognizable task. Skills SHOULD be narrow enough to load only when relevant and SHOULD state authority and stopping conditions once.

The core skills are:

- `igmc-work`: implementation and fixes;
- `igmc-review`: review, diagnosis, and audit;
- `igmc-issues`: local issue drafting and explicitly requested publication;
- `igmc-maintain`: alignment, contract validation, and workflow upgrades.

An MCP server supplies live information, authentication, authorization, or controlled actions. A skill explains when and how to use those tools. Missing MCP access MUST produce an honest boundary, not invented output. Adding an MCP server does not grant permission for external writes.

## 7. Model and cost policy

The default installation performs no model call. The repository MUST NOT create scheduled or unattended AI work.

The global Codex profile maps workload roles to GPT-5.6 family tiers for environments where the user explicitly chooses paid or remote execution. Those mappings are advisory and eval-driven. No profile may trigger a paid call by itself.

Use representative tasks to compare task success, latency, input, output, reasoning, cache-write tokens, and cost per successful task. Preserve workload role and current reasoning effort for the first comparison, then test one level lower. Max effort, pro mode, programmatic tool calling, and multi-agent execution require a demonstrated task fit; they are not defaults.

## 8. Validation

Deterministic validation MUST control:

- contract schema and types;
- required paths and skill entrypoints;
- managed-asset coverage and checksums;
- installer conflict detection;
- migration manifests;
- repository-specific command exit status.

Codex MAY interpret failures and propose repairs. It MUST NOT replace a failing deterministic result with an invented pass.

Builds and headless suites are evidence only. They do not prove live UI, hardware, audio, network, or physical behavior.

## 9. Distribution and migration

Installation is dry-run by default. A plan MUST identify every destination as `create`, `unchanged`, or `conflict` before writing any scaffold file.

Applying a plan requires `--apply`. Conflicts block the complete operation unless the user explicitly supplies `--force`. The installer MUST preflight all paths before writing, preserve existing repository identity when possible, validate requested archetypes, write files atomically, and record a completed migration manifest.

Repository-owned files MUST NOT be overwritten by an ordinary update. Removing an asset from the global standard does not authorize deleting it from a repository.

## 10. Git and GitHub

Git is the durable source and history layer. Commits, pushes, branches, pull requests, and issue publication occur only when requested.

The core scaffold installs no GitHub workflow. Optional adapters MAY provide:

- issue and pull-request templates;
- deterministic contract validation CI.

Optional CI MUST NOT invoke Codex, an AI API, remote agents, issue automation, commits, pushes, or paid services. Organization-wide automation SHOULD use narrowly scoped service identities and immutable action references.

## 11. Issue workflow

Local `tickets/*.md` drafts are the default. Each issue records a concrete outcome, acceptance criteria, validation, sources, and dependencies. Code and current documentation MUST be checked before claiming work is absent or complete.

GitHub publication is an external write and requires an explicit request. Duplicate checking MUST occur before publication. Creating an issue does not authorize assigning an agent or starting remote implementation.

## 12. Security

- Secrets MUST NOT appear in contracts, manifests, skills, or generated reports.
- Destructive commands and broad filesystem operations are blocked by default.
- Unknown skills and tools begin without elevated permissions.
- Repository hooks and migration scripts are executable code and require inspection.
- External data is untrusted input.
- Cost, remote execution, and external-write boundaries remain explicit even when a tool is connected.

## 13. Alignment

Alignment is deterministic and explainable. A score MUST identify each rule, evidence, weight, exemption, and remediation. Critical violations prevent a fully aligned result regardless of the numerical score. Exemptions remain visible and include a reason and review date when applicable.

Quick scans avoid AI calls. Semantic review occurs only when requested and reports uncertainty separately from deterministic failures.

## 14. Completion criteria

A repository is aligned with v2 when:

- `.igmc/repository.json` passes its installed schema;
- required paths and enabled skills exist;
- the declared standard version is current or has a reviewable migration path;
- managed assets are identifiable and conflict-safe;
- local validation commands are accurate;
- no unattended, scheduled, remote, paid, or external action is enabled implicitly;
- durable documentation reflects the current intent, implementation state, and verification boundary.
