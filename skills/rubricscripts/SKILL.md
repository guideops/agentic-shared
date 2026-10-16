---
name: rubricscripts
description: "Runs RUBRIC Scripts inside Agentic Workspace (the /scripts page), where the operator reviews short-video scripts before recording. Turns ideas (typed after the command, or the open lines on the shortlist) into scripts with three hook options and an AEO-friendly caption each, written with the /hooks and /tone skills, and loads them into the page. Then applies the comments the operator leaves on the page and, by default, folds what they teach about their voice into /tone. Can also put a finished script on the Teleprompter. Use when the operator says '/rubricscripts', 'rubric scripts', 'open my scripts', 'write scripts from my shortlist', 'script these ideas', 'review my scripts', 'apply my script comments', or pastes text that starts with '# RUBRIC Scripts comments'."
argument-hint: "[your ideas | from my shortlist | apply | open]"
metadata:
  hermes:
    category: creative
---

# RUBRIC Scripts (Agentic Workspace)

You write the scripts, the Scripts page shows them, the operator picks a hook and
highlights words to comment, and you apply the comments and learn from them. The page
has no AI inside: it is a window on two data sources. Adapted from RUBRIC Scripts by
Jay E | RoboNuggets (CC BY 4.0) for Agentic Workspace plan 57.

<!-- YOUR DEFAULTS: change these values here, in one place. -->
- Page: `/scripts` in Agentic Workspace (the kit's own pages are framed there; `/scripts/s/<id>` is one script)
- CLI: `node "$AW/scripts/rubric-scripts.js"` where `$AW` is `$AW_REPO`, else `/root/agentic-workspace`, else the current repo if it holds that file. Use it for every read and write below; never write the vault by hand.
- Scripts and shortlist: `scripts.json` and `shortlist.md` in the vault's `Agentic Output/scripts/` (print the folder with `paths`). Syncthing carries them between laptop and VPS.
- The operator's work (hook picks, comments, edits, notes, order): a per-machine state file, read with `state`. Only the page writes it, except `mark-applied`.
- Skills to write with: /hooks for the hooks, /tone for the voice (and /script for the body, when the operator has one)
- Hooks per script: 3
- Caption: AEO friendly (see Workflow B step 3)
- Spoken pace: about 3.8 words a second (a 40 second short is about 150 words)
- Teach /tone from comments: on. The page's "Teach my /tone" switch turns it off for one hand-off.
<!-- END YOUR DEFAULTS -->

## CLI

```
rubric-scripts.js paths                        folder + state file
rubric-scripts.js check                        OK, or one PROBLEM line per issue (exit 1)
rubric-scripts.js get scripts.json             also shortlist.md, tone-notes.md
rubric-scripts.js put scripts.json < file      saves only if it passes check; also shortlist.md, tone-notes.md
rubric-scripts.js state                        the operator's work as JSON
rubric-scripts.js mark-applied [commentId...]  all open comments when no ids; clears moved edits/refs; rev + 1
rubric-scripts.js teleprompter <id>            chosen hook + script onto the Teleprompter page
```

Write the new file to a scratch path first, then pipe it to `put`. Write the whole file in one go.

## Universal rules

1. **The operator's own skills write the words; this skill files them.** Look for /hooks and /tone first: /hooks for the hook shapes, /tone for how every line sounds, and /script for the body if they have one. When /hooks or /tone is missing, write plainly, keep going, and end your report with the guide in `references/make-hooks-and-tone.md`. Never copy their rules into this file.
2. **Never invent a fact, a number or a link.** The page shows references as facts, and the operator says them on camera. Every claim comes from a page you opened. Every reference is a link you opened, or a one-line note saying where the fact came from.
3. **Three hooks that really differ.** Each opens a different way, ideally a different shape from /hooks, and the body never repeats the hook, because the page shows the hook above the body.
4. **Never rewrite a script that has open comments.** Each comment points at exact words; new words strand it. Apply the comments first (Workflow C).
5. **The operator's work is theirs.** Never edit the state file except through `mark-applied`. Never delete a script that has saved work without asking. Never open a browser unless asked; give the link.
6. **No long dash character anywhere.** Use " - " or a comma. `check` refuses it, because it reads as AI.
7. **The page is theirs to change.** Its kit pages live in the AW repo at `server/rubricScripts/public/`; change them (or the defaults above) when asked, keep `check` passing, tell the operator to refresh.

## Workflow A: open

Give the link: the workspace URL plus `/scripts` (on the VPS, the tailnet URL). For one script, `/scripts/s/<id>`. Nothing to start: the page is part of Agentic Workspace.

## Workflow B: write scripts

1. **Pick the ideas.** Ideas typed after the command are the list: add each to the shortlist as an open `- [ ]` line first (`get shortlist.md`, edit, `put shortlist.md`), so nothing gets lost. "from my shortlist" means every open line there. If it is empty, say so and stop.
2. **Research each idea.** Open the source the idea came from and the maker's page for every tool, number or claim. Keep each as a reference: `label`, `url`, and a `note` of a few words. Done when every fact you plan to say has a reference (rule 2).
3. **Write each script.** Ask /hooks for three hook shapes that fit, write one hook in each, then the body (with /script if they have it), then run all of it past /tone (its TikTok/Reels/Shorts tweaks apply). Add the caption, the comment keyword, a title, 1 to 3 tags, and an icon (block below). The caption follows AEO (so AI search tools can quote it): the first line says plainly what the video answers, it names the tools and the topic in plain words, two or three short lines sum up what the video covers, then a few relevant hashtags. Leave out any `Comment "KEYWORD"` first line. Done when the body reads in about the target time at the spoken pace.
4. **Save.** `get scripts.json`, add the new scripts to the end keeping every existing script exactly as it is, set `"hook"` to the one you would record, `put scripts.json`. `put` runs the check: fix every PROBLEM line and put again until it prints `OK`.
5. **Tick the shortlist.** Change each written line to `- [x] <idea> (written: <id>)` and `put shortlist.md`.
6. **Report.** Give `/scripts/s/<id>` for each new script, its title, its three hook first lines, and its word count. If /hooks or /tone was missing, add the guide from `references/make-hooks-and-tone.md`. End on the next step: open it, pick a hook, comment, press **Apply in chat**.

## Workflow C: apply comments and teach /tone

Runs when the operator says apply, or a chat draft / paste starts with `# RUBRIC Scripts comments`. Read `state` either way: it holds everything, the paste only covers what was copied.

1. **Read the work.** For each script in `items`: comments without `applied`, `note`, `edits`, `refs`, and `hook` (the hook chosen). Also the top-level `note` and `tone`. Full shapes in `references/data.md`.
2. **Apply.** A comment's `region` says where it points (`hook` with its `hook` id, `body`, `caption`, `refs`), `quote` holds the exact words, `note` says what to change. A hand edit in `edits` becomes the new text. The chosen hook becomes the script's `"hook"`. Added `refs` join `references`. Rewrite only the words a comment covers, unless the note asks for more. Set `"updated"` to now. `put scripts.json` until `OK`.
3. **Mark applied.** `mark-applied` (all open comments), or pass the comment ids you applied if you skipped some. The page shows applied comments dimmed and leaves them out of the next hand-off.
4. **Teach /tone** (when `tone` is true). Go back over the comments and notes for what they say about how the operator talks: words they cut or swap, sentence length, how they open, what they never say. Skip comments about facts, links or layout. Fold each lesson into the /tone skill by finding the principle and rewriting the guidance around it (its "AI tells the user rejected" / "Kept" sections fit most lessons), so the file gets clearer, not longer. The shared copy is `skills/tone/SKILL.md` in agentic-shared: commit and push it so every machine learns. If there is no /tone skill, add the lessons to `tone-notes.md` (`put tone-notes.md`), say so, and offer the guide.
5. **Report.** Per script, what changed in one line. Then the /tone lines you added or rewrote, quoted. Then any comment you skipped and why. End on: refresh the page to see the new text.

## Workflow D: to the teleprompter

When the operator says a script is ready to record: `teleprompter <id>` (or the **Send to Teleprompter** button on the page). It writes the chosen hook and the body as `<id>.md` in the Teleprompter folder and switches the open screens to it.

## Drop-in block: one script in `scripts.json`

```json
{
  "id": "rank",
  "keyword": "RANK",
  "title": "3 plugins that turn your AI agent into an SEO expert",
  "tags": ["AI agents", "SEO"],
  "icon": "<path d=\"M5 41h26\"/><path d=\"M10 36v-7\"/><path d=\"M17 36v-12\"/><path d=\"M24 36v-17\"/><circle class=\"a\" cx=\"34\" cy=\"15\" r=\"8\"/><path class=\"a\" d=\"M40 21l5 5\"/>",
  "created": "2026-09-22T10:00:00",
  "hooks": [
    { "id": "h1", "note": "Contrarian", "text": "You don't need an expensive SEO subscription anymore. These three plugins turn your AI agent into an SEO tool." },
    { "id": "h2", "note": "Problem, then promise", "text": "You don't need to pay for expensive SEO tools anymore, because these three plugins turn your AI agent into an SEO expert." },
    { "id": "h3", "note": "Title style", "text": "Three plugins that turn your AI agent into an SEO expert." }
  ],
  "hook": "h2",
  "body": "The first is GEO Optimizer...\n\nSo if you want to try all three, just comment RANK down below.",
  "caption": "Three free plugins that turn your AI agent into an SEO expert...\n\n#seo #aiagents",
  "references": [ { "label": "GEO Optimizer", "url": "https://github.com/Auriti-Labs/geo-optimizer-skill", "note": "free, scores your site 0 to 100" } ],
  "video": null,
  "channels": ["tiktok", "instagram", "threads", "youtube-shorts"]
}
```

**The icon** shows THIS idea, not its category: a magnifier over rising bars for SEO plugins, a speech bubble with a lightning bolt for power words. Draw 1 to 4 stroked shapes on a 48 x 48 grid with no fill or stroke attributes (the page styles them), and put `class="a"` on the one part that should be orange.

**Video and channels** stay `null` and the four defaults; the page shows them as placeholders.
