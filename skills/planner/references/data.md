# RUBRIC Planner data

One file: the vault's `Agentic Output/planner/planner.md`, which holds the kit's planner.json in a fenced json block. Read and write it only with `node scripts/planner.js get` / `put` in `/root/agentic-workspace`. The page reads it on every load and when the window regains focus, so a change you save shows up without a restart.

## `planner.json` (the app and you both write it)

```
{ "app": "rubric-planner", "format": 1, "owner": "<name>",
  "rev": 7,                                    goes up by 1 on every save; add 1 when you change this file
  "updated": "2026-10-20T05:00:00.000Z",       the app sets this
  "items": [ {
    "id":    "s1"                              any unique text; never change it
    "title": "Deep work: client blueprint"     what the cards show
    "date":  "2026-10-20" | null               null = the Inbox (no day yet)
    "start": "09:00" | null                    24 hour; null = a task with no time
    "end":   "11:00" | null                    after start; null with a start = 30 minutes on the timeline
    "done":  false
    "top":   true                              in that day's Top 3 (at most 3 per day)
    "tag":   "client"                          one word, optional
    "note":  "..."                             optional
    "by":    "agent" | "user"                  who added it
  } ],
  "periods": {                                 goals and a note per period, all optional
    "2026":       { "goals": [ { "id": "g1", "text": "...", "done": false } ], "note": "year theme" },
    "2026-10":    { "goals": [...], "note": "..." },      month
    "2026-W43":   { "goals": [...], "note": "..." },      ISO week (Monday start)
    "2026-10-20": { "goals": [],    "note": "day note" }  day
  },
  "handoff": { "note": "what the user asked you to do in the app" }
}
```

Run `node scripts/planner.js check` after every write (`put` already runs it). It names each problem by item and field.

## What the app tidies

The app never breaks on an odd file: a duplicate id gets a suffix, an unreadable date sends the item to the Inbox, an end before its start is dropped. Each fix shows in a yellow line at the top of the page, so the user sees what to ask you to correct. A file that is not valid JSON at all is not overwritten: the app refuses to save until `node scripts/planner.js check` passes.

## Saving and the stale tab

Every save from the page sends the `rev` it last saw. If the file moved on (you wrote it, or another tab did), the server refuses the save, and the page loads the newer file and asks the user to make their last change again. So always add 1 to `rev` when you write, and write the whole file in one go.
