---
name: fitness-log
description: "Log workouts, generate training plans, and track progress trends. Saves to `domains/productivity/fitness/` and surfaces weekly summaries."
metadata:
  hermes:
    category: productivity
---

# fitness-log

**Trigger**: `/fitness-log` or "log workout", "fitness update", "track my training"
**Domain**: productivity
**Automation**: local (on-demand)

## Description
Log workouts, generate training plans, and track progress trends. Saves to `domains/productivity/fitness/` and surfaces weekly summaries.

## Instructions
1. Ask user (or accept inline): workout type, exercises, sets/reps/weight, duration, notes.
2. Append to `domains/productivity/fitness/log.md` with today's date.
3. After logging, check last 7 days of logs:
   - Volume per muscle group
   - Progressive overload trend (weight/reps increasing?)
   - Rest days vs. training days
4. Surface brief summary: "7-day: 4 sessions, chest +5% volume, missed legs."
5. If user says "plan next week" → generate weekly training plan based on log history and goals in `domains/productivity/fitness/goals.md`.
6. Log to `domains/productivity/learnings.md`.

## Input
Inline: `/fitness-log push: bench 4x8@80kg, dips 3x12, ohp 3x10@60kg`
Or interactive: Codex asks each field.

## Output
Appended to `domains/productivity/fitness/log.md`:
```markdown
## 2026-05-08
- Type: Push
- Bench Press: 4x8 @ 80kg
- Dips: 3x12 BW
- OHP: 3x10 @ 60kg
- Duration: 55 min
- Notes: ...
```

## Automation
None by default. Can schedule weekly summary to dashboard via cron.
