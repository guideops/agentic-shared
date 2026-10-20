---
name: planner
description: Runs RUBRIC Planner, the small local app where the user plans their day, week, month and year. Starts the app, plans a day or a week for them (time blocks, Top 3, goals) by writing the planner file, carries out what they ask in the app's "Hand to agent" box, and writes reviews into the day, week, month or year notes. Use when the user says "/planner", "open my planner", "plan my day", "plan my week", "plan tomorrow", "review my week", "what's on today", "move X to Friday", "planner apply", or pastes text that starts with "# RUBRIC Planner brief".
metadata:
  hermes:
    category: productivity
argument-hint: "[open | plan day|week | review day|week|month | apply | <anything to add or move>]"
---

# RUBRIC Planner

The user plans in the Planner page; you plan from the vault. The page has no AI inside: it is a window on one file, `planner.json` (stored as `planner.md`), and both of you write it. You never fight over it because every write carries `rev`, and the app refuses a save made on an old `rev`.

<!-- YOUR DEFAULTS: change these values here, in one place. -->
- Where the plan lives: the Agentic Workspace vault, `Agentic Output/planner/planner.md` (the kit's planner.json inside one fenced json block). Never open that file by hand: use the CLI from the workspace repo (`/root/agentic-workspace`).
- CLI: `node scripts/planner.js get | put | check | today` (run from `/root/agentic-workspace`). It is the only write door.
- Page: the workspace's `/planner` (full screen: `/planner/app`).
- Working hours: 08:00 to 18:00. Deep work goes in the morning unless the user says otherwise.
- Top 3: at most three starred items per day.
- Week starts Monday. Week keys are ISO weeks (`2026-W43`).
- Write reviews with /tone when the user has it.
<!-- END YOUR DEFAULTS -->

## Universal rules

1. **Never move or delete what the user made without being asked.** [Their plan is theirs; you add to it.] Items you add get `"by": "agent"`. You may change a `"by": "user"` item only when the ask names it.
2. **Never invent a commitment.** [A time block reads as a promise.] Every item you add comes from the ask, a goal, the Inbox, or an existing item. Say which in your report.
3. **Respect the shape of a day.** No overlaps with existing timed items unless asked, nothing outside working hours unless asked, at most 3 `top` per day (`planner.js check` warns past 3).
4. **Read before you write, write the whole file once.** `node scripts/planner.js get`, change it in memory, add 1 to `rev`, pipe the whole file to `node scripts/planner.js put`. Never hand-edit a slice. If the page saved in between, `put` refuses (rev is not disk + 1): read again and redo the change.
5. **No long dash character anywhere.** Use " - " or a comma. `planner.js check` refuses it.
6. **The app is theirs to change.** When they ask (a different start hour, a new view, a field), change the defaults above or the files in `/root/agentic-workspace/server/planner/public/` (colours are the token block at the top of `app.css`), keep `node scripts/planner.js check` passing, and tell them to refresh (a server-side change needs a workspace restart).

## Workflow A: open the app

1. From `/root/agentic-workspace` run `node scripts/planner.js today`. If it prints JSON, the vault and the plan are reachable. If it errors with "No Obsidian vault", tell the user to set the vault path in Setup and stop.
2. The page is the workspace's **Planner** (`/planner`, sidebar Work group; full screen at `/planner/app`). It is served by the workspace server, so there is nothing else to start. If the workspace itself is down, say so; do not start a second server.
3. Give the route, with the view in the link when it helps: `/planner/app#/week/2026-10-20`. Done.

## Workflow B: plan a day or a week

1. **Read.** `planner.json`: the period's items, the goals for the day, week, month and year that contain it (`periods`), the Inbox (items with `"date": null`), and the notes. Done when you know what is fixed and what is free.
2. **Choose.** Pick what serves the goals first: open goals for the week, then the month. Pull Inbox items that fit. Done when every pick has a reason you can name.
3. **Block.** Give each pick a `date`, and a `start` and `end` when it needs focus time. Fill free slots inside working hours, deep work in the morning. Star up to 3 per day as `top`. New items look like the block below. Done when nothing overlaps.
4. **Save and check.** Write the file (rule 4, `put` runs the check), then run `node scripts/planner.js check`. Fix every PROBLEM line. Done when it prints `OK`.
5. **Report.** Per day: what you added, its time, and why (which goal or Inbox item). Then the route from Workflow A. End on: open it, drag anything that is wrong, then hand back.

## Workflow C: apply the hand-off

Runs when the user says apply, or pastes text that starts with `# RUBRIC Planner brief`. Read `handoff.note` in the file either way; the paste only shows one view.

1. **Read the ask** in `handoff.note` (or the paste's `## Ask`). Ids in braces in a paste are item ids. Done when you can say the ask back in one line.
2. **Do it** with Workflow B's rules: moving names `date`/`start`/`end`, finishing sets `done`, new things are new items, goals go in `periods[<key>].goals` as `{ "id": "g<something unique>", "text": "...", "done": false }`.
3. **Clear the ask.** Set `handoff.note` to `""` so the next hand-off starts clean. Save and check (Workflow B step 4).
4. **Report** what changed in one line per item, then anything you skipped and why. End on: refresh the app.

## Workflow D: review a period

1. Read the period's items (done and not done) and its goals.
2. Write a short review into `periods[<key>].note` under any text the user wrote, starting with a line `Review (agent, YYYY-MM-DD):`. Three to five lines: what got done against the goals, what slipped and where it went, one thing to change next time. Use /tone when they have it.
3. Offer, do not do: carry undone items to the next period. Only move them when the user says yes.
4. Save and check. Report the review text.

## Drop-in block: one item in `planner.json`

```json
{ "id": "a7k2", "title": "Deep work: proposal draft", "date": "2026-10-22", "start": "09:00", "end": "11:00",
  "done": false, "top": true, "tag": "client", "note": "For goal: Close 1 new client", "by": "agent" }
```

`id` is any unique text (keep it short). `date` null puts it in the Inbox. `start` null makes it a task with no time. Full shapes in `references/data.md`.
