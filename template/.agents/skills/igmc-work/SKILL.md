---
name: igmc-work
description: Implement or fix repository behavior with scoped edits and proportionate local validation. Use for requested code, configuration, or documentation changes; not for review-only requests.
---

# IGMC work

1. Read `.igmc/repository.json`, the nearest `AGENTS.md`, and only the relevant design/code paths.
2. Trace the current behavior before editing. Preserve unrelated work and existing public contracts unless the request requires a change.
3. Make the smallest coherent implementation. Update durable documentation only when intent, behavior, contracts, or verified status changed.
4. Run the most focused declared validation first, then broader local checks in proportion to risk. A build or headless suite does not prove live UI, hardware, audio, network, or physical output.
5. Report the outcome, files changed, commands and results, and any remaining live verification.

Do not create tickets, commits, pushes, pull requests, remote tasks, scheduled work, paid API calls, or external writes unless the user explicitly requested them. Ask only when a missing decision would materially change the result.
