---
name: goal-tracker
description: "Weekly goal check-in across all domains. Surfaces progress, flags blocked goals, and generates next-week priorities. Reads from all domain `learnings.md` files."
metadata:
  hermes:
    category: productivity
---

# goal-tracker

**Trigger**: `/goal-tracker` or "review goals", "goal check-in", "weekly review"
**Domain**: productivity
**Automation**: remote (weekly Sunday review via cron)

## Description
Weekly goal check-in across all domains. Surfaces progress, flags blocked goals, and generates next-week priorities. Reads from all domain `learnings.md` files.

## Instructions
1. Load goals from `domains/productivity/goals.md`.
2. Scan all domain `learnings.md` files for the past 7 days.
3. For each goal:
   - Status: on-track / behind / blocked / complete
   - Evidence: what was done this week toward it
   - Gap: what's missing
4. Generate weekly review report:
   - Top 3 wins
   - Top 3 blockers
   - Adjusted priorities for next week
   - Specific action items per domain
5. Save to `domains/productivity/reviews/YYYY-WW.md`.
6. Update `domains/productivity/goals.md` with new status tags.

## Input
None (scheduled). Or `/goal-tracker --week 2026-W19` to review specific week.

## Output
```markdown
---
domain: productivity
date: YYYY-MM-DD
type: weekly-review
week: YYYY-WW
---
# Weekly Review — Week WW
## Wins
## Blockers
## Goal Status
| Goal | Domain | Status | Evidence |
|------|--------|--------|----------|
## Next Week Priorities
## Action Items
```

## Automation
Remote — GitHub Actions cron (Sunday 20:00):
```yaml
on:
  schedule:
    - cron: '0 20 * * 0'
```
Reads: all `domains/*/learnings.md`
Writes: `domains/productivity/reviews/`
