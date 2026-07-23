---
name: calibrate
description: In-session self-improvement. Reviews the current conversation for corrections, preferences, and patterns, then suggests specific skill/setup updates. Triggers on "calibrate", "what can you improve", "update your skills", "what did we learn", "tune up". Lite mode: "calibrate lite" or "/calibrate lite" — fast 1-3 suggestion sweep for shorter sessions.
credits: Adapted from robonuggets/skills (github.com/robonuggets/skills); Targets in this setup section localised.
---

# Calibrate: In-Session Self-Improvement

## What This Does

Reviews the current conversation and suggests specific updates to skills, instruction files, memory, or workflows based on what just happened. The user picks which suggestions to apply.

## Two modes

- **Full (default)** — deep scan of the whole conversation, max 7 suggestions. Use at end of long sessions or after multiple corrections.
- **Lite** — triggered by `calibrate lite` or `/calibrate lite`. Fast 1-3 suggestion sweep for shorter sessions. Skips deep pattern matching. Just surfaces the loudest 1-3 things from the most recent 10-20 turns. ~80% fewer tokens.

If a lite sweep returns "nothing to calibrate", that's a valid output — say so in one line and stop.

## When to Use

- End of a work session
- After a task with multiple corrections
- When the user says "calibrate", "what can you improve", "tune up", "update your skills"

## Lite mode shortcut

If trigger is `calibrate lite` / `/calibrate lite`:

1. Scan only the last 10-20 turns (not the whole session)
2. Look for at most 3 things — corrections that happened, preferences revealed, repeated patterns
3. Output max 3 numbered suggestions in the same `[TARGET: file] — [what]` format
4. If nothing meaningful surfaced: respond `Clean — nothing to calibrate` in one line. Don't pad.

Lite is the right call when:
- Session was short (under ~20 turns)
- Most of the work was unmemorable (routine queries, lookups)
- You just want a quick "anything I should fix?" without a deep audit

## Process

### Step 1: Scan the Conversation

Review everything in the current session. Look for:

- **Corrections** — where the user said "no", "wrong", "not that", "I meant X"
- **Preferences revealed** — format choices, tone adjustments, workflow preferences
- **Process gaps** — steps you missed that a skill should encode
- **Repeated patterns** — same type of correction more than once = systemic issue
- **Things that worked** — approaches the user confirmed or accepted without pushback

### Step 2: Match to Updateable Targets

For each finding, identify WHERE the fix belongs:

- **Skill file** — if the issue is about how a specific task is executed
- **Instruction file (CLAUDE.md or equivalent)** — if the issue is about general agent behavior or rules
- **Memory** — if it's a preference or context that should persist across sessions
- **Workflow / scheduled task** — if it's about when or how automated tasks run
- **Tone / style file** — if it's about voice or writing style (rare, check with the user first)

### Step 3: Present Suggestions

Format as a numbered list. Each suggestion should be:

```
[number]. [TARGET: filename] — [what to change]
Brief why: [one sentence explaining the pattern that triggered this]
```

Example:
```
1. SKILL: thumbnail-gen — Add rule to always generate 3 variations, not 1
Brief why: User asked for alternatives twice this session after I gave a single option.

2. CLAUDE.md — Add "never suggest routing to other agents" to red lines
Brief why: User corrected me when I suggested handing off.

3. MEMORY — Save preference: user prefers kebab-case for all file names
Brief why: User renamed two files I created in camelCase.
```

Rules for suggestions:
- **Max 7 suggestions.** If you find more, prioritize by impact (repeated corrections > one-offs).
- **Be specific.** Not "improve writing quality" but "add rule: no sentences over 20 words in posts."
- **Only suggest changes the data supports.** Don't pad with generic improvements.
- **If nothing meaningful to update, say so.** "Clean session — nothing to calibrate" is a valid output.

### Step 4: Apply

Wait for the user to respond with which numbers to apply (e.g. "do 1 and 3", "all", "skip 2").

Then:
1. Make the changes to the target files
2. Confirm each change with the file path and a one-line summary
3. If updating a skill, re-read it after editing to verify it's coherent
4. If updating memory, follow your memory system's rules (write file + update any index)

### Step 5: Done

No follow-up needed. Changes are live for the next time the skill/rule is invoked.

## What NOT to Suggest

- Changes that are already in the relevant skill or instruction file (check first)
- Generic "best practices" not grounded in this session's data
- Temporary fixes for one-off situations
- Changes to files outside your write scope

## Targets in this setup

Where fixes actually live here (use these paths in `[TARGET: ...]` suggestions):

- **Skills** — `~/ai-workspace/claude-projects/agentic-shared/skills/<name>/SKILL.md`. Edit in the shared repo, never through the `~/.claude/skills/` symlink target confusion — same file, but reference the repo path so the change is visibly a repo change to commit.
- **Instructions** — `~/.claude/CLAUDE.md` (global) or the project's `CLAUDE.md`.
- **Hooks / settings** — `~/.claude/settings.json`. Hook script sources live in `~/.claude/hooks/`.
- **SOPs** — vault `05 Agent/SOPs/SOP-NN *.md`. Vault writes must be announced in chat with the full vault path (transparency rule).
- **Memory** — claude-mem captures observations automatically; only suggest an explicit memory write for durable *preferences or feedback rules*, not facts claude-mem already recorded.

Pairing: `/checkpoint` saves **project** state; `/calibrate` tunes the **agent**. End of a heavy session, run both — checkpoint first, calibrate second.

Repo hygiene: skill edits land in agentic-shared as uncommitted changes — remind the user to commit so laptop/VPS pick them up (SOP-01).
