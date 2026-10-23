---
name: recos
description: Audits the user's own agent setup across ARMS (Apps, Routines, Memory, Skills) plus the workflows they repeat, then writes the changes that would help most into RUBRIC Recos (recos.js in the Documents folder), the /recos page in Agentic Workspace where the user skips, finishes or carts each one. Use when the user types "/recos", or says "refresh my recos", "refresh RUBRIC Recos", "audit my setup", "how can I improve my setup", "what should I fix in my agent", "find ways to save tokens", and once when the Recos page is still empty. Also offers a weekly routine that refreshes the recos.
---

# Recos

You look at how this user really works with you, then write the few changes that would help them most. They read the result in RUBRIC Recos, a page on their own computer, and pick what happens.

## Rules for every run

1. **Look, don't touch.** The audit only reads. The one file you write is `recos.js`, because the user decides which recos happen.
2. **Start from what you know.** You already know this user and this workspace from your memory and past sessions. Use that first, and read a file only when a reco needs evidence you don't have yet. A full crawl burns the tokens these recos are meant to save. **No history yet?** Read these, in this order: the instructions file that loads every session, the memory or notes index, the skills folder (names and line counts only, then open the few that look wrong), the routines or scheduled tasks list, and any session logs. Ask the user for what you can't find.
3. **Evidence or it doesn't ship.** Every reco names what you saw: a file and its size, a correction that came back three times, a routine that failed twice. A tip that fits any setup is noise.
4. **Keep their ids.** A reco that is still true keeps its old `id`, so a skip stays a skip and a done mark stays done.
5. **Private stays private.** Never copy a key, password or token into a reco. Name the file it lives in instead.

## Find the files

RUBRIC Recos is the `/recos` page in Agentic Workspace (AW), adapted from RUBRIC Recos by Jay E | RoboNuggets (MIT). There is no app to start. The AW command prints where the files are:

```
node "$AW/scripts/recos.js" paths    recos.js and state.json (in the Documents folder, ~/Documents/Hermes/recos/)
node "$AW/scripts/recos.js" check    OK, or one PROBLEM line each
node "$AW/scripts/recos.js" state    the user's skips, done marks and comments
```

`$AW` is `$AW_REPO`, else `/root/agentic-workspace`, else the current repo if it holds `scripts/recos.js`.

## Steps

```text
Recos progress:
- [ ] 1 Read recos.js and state.json
- [ ] 2 Audit the five areas
- [ ] 3 Pick the recos
- [ ] 4 Write recos.js
- [ ] 5 node "$AW/scripts/recos.js" check passes
- [ ] 6 Tell the user in 3 lines
- [ ] 7 First run only: offer the weekly routine
```

1. **Read what is there.** Note every current id, and which ones `state.json` lists under `skipped` and `done`. Its `comments` are the user's notes on recos: fold them into this run. One comment looks like this (`label` is the reco title, `target` is its id, with a `pri-` prefix when it was made in the Priority group, and `status: "applied"` means it is already handled):

   ```json
   { "id": "hmvbw7ou2mc92", "target": "s-split-posts", "label": "Split the posts skill in two", "quote": "loads every time", "nth": 0, "text": "Say how many lines it is now", "created": 1792211096954 }
   ```
2. **Audit** with [references/audit.md](references/audit.md): Apps, Routines, Memory, Skills, then workflows the user repeats that no skill covers yet. Done when each area has findings with evidence, or one line saying nothing is worth fixing. A pillar with no evidence gets 0 recos; that is a fine result, not a gap to fill.
3. **Pick up to 20 recos, usually 8 or more.** Fewer is fine when that is all the evidence supports; never pad with generic tips. Rank by the gain to the user, not by how easy the work is for you. Drop what is already true in the setup and any duplicates. A done mark that proved false keeps its reco, with the new evidence. Skipped recos can stay in the file, since the page hides them, and keeping them stops you suggesting the same thing under a new id. Mark the top 3 to 5 `pri: "high"` with `rank` 1, 2, 3 in order.
4. **Write `recos.js`** in the shape described at the top of that file. Replace only the `window.RECOS = { ... };` block, so the header comment stays. Set `built` to today's date and `footer` to one line on when and how this refresh was made.
5. **Check.** Run `node "$AW/scripts/recos.js" check`. If it fails, return to step 4, fix what it names, and run it again.
6. **Tell the user** in 3 lines at most: how many recos per pillar, the top one in a sentence, and where to see them: the `/recos` page in Agentic Workspace (Command Centre, Micro Apps, RUBRIC Recos).
7. **First run only, offer the weekly routine** (last section).

## Writing a reco

The user reads these fast and picks. Every word should help that pick.

- **Plain words.** Short sentences, one idea each, for someone smart who is not technical. Common agent words (skills, hooks, routines, memory) are fine. No em dashes: use " - " or a comma.
- **`title`**: verb first, under 10 words. "Split the posts skill in two", not "Posts skill size".
- **`benefit`**: the gain for the user, then the evidence. "Post jobs start faster and cost less. The skill is 900 lines and loads every time."
- **`action`**: you, in the first person, saying what you would do. "I move the examples into a reference file."
- **`effort`** and **`pri`**: low, mid or high. No times, because a time estimate for agent work is a guess.
- **`saves`** and **`savesNote`**: only on recos that cut tokens on every run from then on (smaller files that load every session, fewer redo jobs, a cheaper model for a simple routine). Leave both out on the rest, so the green bar means something.
- **`touches`**: the skills or files the work changes, 3 at most, exact names.
- **`source`**: exact paths and numbers. It rides along in the cart for whoever does the work.
- **`svg`**: a small line drawing of this reco on a 48x48 grid, 2 to 4 shapes, with 1 or 2 strokes marked `class="a"` for the pillar colour. Draw the thing itself (scissors for a split, a clock for a routine). Use only `path`, `circle`, `rect`, `line`, `polyline`, `polygon` and `ellipse` (a `g` to group them is fine), strokes only, no fill or colour attributes: the page drops anything else.
- **`id`**: pillar letter, a dash, two or three words: `s-split-posts`, `r-weekly-backup`.

## The weekly routine

Offer it once, in one line: "I can refresh your recos every week, so new ones are waiting for you. Want that?" Set it up only on a yes, with the scheduler you have:

- If your agent has scheduled tasks or routines built in, create a weekly one with the prompt `/recos`.
- If it doesn't, use the computer's own scheduler (Task Scheduler on Windows, cron or launchd on Mac and Linux) to start your agent without a window, with that same prompt.

Pick a quiet time with the user. The run only writes `recos.js`, so it is safe to run unattended. Tell them how to turn it off.
