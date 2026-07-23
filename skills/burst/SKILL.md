---
name: burst
description: Generate N meaningfully different variations of one deliverable so the user picks the one that lands instead of iterating on a single guess. /burst 5 <thing> makes 5 numbered variations. Trigger also on "give me options", "variations", "burst this", "show me a few takes".
credits: Concept from RoboNuggets (youtube.com/watch?v=UpgjdQJShWg); skill not in his public repo, written for this setup.
---

# Burst

One attempt is a guess. N variations is a menu. Generate the spread, let the user point at the winner.

## When invoked

`/burst N <task>` → exactly N variations (clamp 2–10). `/burst <task>` bare → you pick N: 3 for expensive outputs (full pages, long docs), 5 default, up to 7 for cheap ones (headlines, names, one-liners).

Applies to anything with a taste dimension: copy, headlines, names, layouts, color directions, component designs, email drafts, hooks, slide titles, architectures, API shapes. Not for tasks with one correct answer — if the task is deterministic (fix this bug, compute this), say "nothing to burst" and just do it.

## Rules for the spread

- **Meaningfully different, not reworded.** Each variation takes a different *angle* — different tone, structure, metaphor, audience, or tradeoff. If two variations could be described the same way in one sentence, they're the same variation; replace one.
- **Label the angle.** Each variation gets a number and a 2–5 word angle tag so the user can reason about the spread, not just the instances.
- **Full quality each.** No throwaway padding variations to hit N. Every one must be shippable as-is.
- **State your pick.** After the list, one line: which number you'd ship and why. User is free to ignore it.

## Output format

```
**1. [angle tag]**
<variation>

**2. [angle tag]**
<variation>
...

My pick: 3 — <one-line reason>.
```

For file-based outputs (HTML pages, components), write numbered files (`thing-v1.html`, `thing-v2.html`...) instead of inline dumps, and list them with angle tags. Open them for preview when a browser/preview tool is available.

## After the pick

User replies with a number, or a combination ("2 but with 4's ending"), or free text direction. Then:

- Single pick → that becomes THE deliverable; delete/ignore the losers (ask before deleting files)
- Combination → merge as directed, show result
- "None" → ask for one sentence on what's missing, burst again with that constraint; don't regenerate blind

## Anti-patterns

- Five rewordings of one idea wearing different hats
- Ranking all variations — you get one pick, not a leaderboard
- Bursting when the user already specified the angle precisely — just build it
- Asking "want me to make variations?" — if invoked, burst; if not invoked but the task screams taste-dependence, make ONE and offer "want a burst of alternatives?"
