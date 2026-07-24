---
name: session-kanban
description: Register substantive work on the Hermes kanban board (mirrored to the AURA wall): create a card at work start, comment milestones, complete with a summary.
---

# Session Kanban

When beginning a substantive unit of work in a repo — a plan, feature, or multi-step task — register it on the Hermes kanban board.

1. Determine the absolute repo path and use its directory basename as the project slug.
2. Ensure the local Hermes project record exists:
   - Run `hermes project list`.
   - Compare the first whitespace-delimited token of each line with the repo basename.
   - If none matches, run `hermes project create "<repo basename>" --slug <repo-basename> --primary <abs repo path>`.
   - This is a local grouping record only, not a repository or GitHub project.
3. Create the card:
   - Run `hermes kanban create "<short title>" --project <repo-basename> --created-by <claude-code|codex|hermes> --idempotency-key plan:<kebab-slug-of-title> --json`.
   - Parse and remember the returned task id.
   - The idempotency key makes re-runs safe.
   - Optionally add `--priority N`: 1 low, 2 medium, 3 high, 4 urgent.
4. At meaningful milestones, run `hermes kanban comment <task-id> "<one-line progress note>"`.
5. When the work lands, run `hermes kanban complete <task-id> --summary "<what shipped + how verified>"`.
6. If blocked on the user, run `hermes kanban block <task-id> --reason "<why>" --kind needs_input`.
7. When work resumes, unblock the task before continuing.

Keep comments brief, factual, and tied to meaningful progress. Do not create cards for trivial one-step requests.
