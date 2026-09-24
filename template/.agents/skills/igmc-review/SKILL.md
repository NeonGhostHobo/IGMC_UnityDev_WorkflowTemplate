---
name: igmc-review
description: Review, diagnose, or audit repository changes using concrete evidence and local checks. Use for code review, architecture review, regression diagnosis, or verification reports; not for implementation unless explicitly requested.
---

# IGMC review

1. Read `.igmc/repository.json`, relevant design material, the change diff, and the actual implementation path.
2. Check behavior and contract correctness before style. Then check edge cases, failure handling, security, maintainability, and verification gaps.
3. Run safe, read-only or non-destructive local checks when they can confirm a finding.
4. Report only material findings, ordered by severity, with file locations and concrete impact. Distinguish confirmed defects from uncertainty and missing live verification.
5. If no material findings remain, say so and list residual verification limits.

Review requests do not authorize edits, external writes, paid services, remote tasks, or publication.
