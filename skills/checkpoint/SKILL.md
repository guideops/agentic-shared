---
name: checkpoint
description: Session-end vault update or project resume. /checkpoint saves session state, decisions, and canvas changes to the Obsidian project docs. "/checkpoint resume <name>" loads where you left off. Trigger also on "save state", "checkpoint this session", "resume <project>", "where did we leave off".
---

# Checkpoint

Two directions: **save** (session end) and **resume** (session start). Keeps the vault project docs in `02 Projects/<Name>/` truthful.

Vault root, resolved per machine in order: (1) `$CLAUDE_VAULT` env var; (2) known paths — `C:\Users\pawar\Documents\ajqcd-zaozt`, `~/Documents/ajqcd-zaozt`, `~/ajqcd-zaozt`, `~/vault/ajqcd-zaozt`; (3) Windows: `%APPDATA%\obsidian\obsidian.json` (vault folder `ajqcd-zaozt`). No vault found → **no-vault machine** (e.g. VPS worker): say so, skip all vault writes, and instead print the checkpoint summary as text for the user to paste or sync later. Never write vault files to a guessed path.

## /checkpoint (save)

### 1. Identify the project

From cwd repo name, conversation context, or ask. Match against folders in `02 Projects/`. If no project folder exists, offer `/project-kickoff` instead.

### 2. Gather what actually happened

- `git log --oneline` since session start + `git status` in the working repo
- Decisions made this session (stack changes, architecture pivots, rejected approaches)
- What was completed, what is mid-flight, what blocked

### 3. Update `STATE.md` (always)

Overwrite the Last session / Done / Next / Blockers sections. Keep prior "Done" items only from the current work phase — STATE.md is a resume note, not a changelog. Update `updated:` frontmatter and `## Active playbook` (which `plans/NN-*.md` is in progress, if any).

### 4. Append to Decisions log (only if decisions were made)

New `### D-NNN` entries in `<Name>.md` using the ADR format (Chosen / Rejected / Why / Revisit if). Never edit past entries — if a decision was reversed, add a NEW entry referencing the old one ("supersedes D-003").

### 5. Patch `<Name>.canvas` (ONLY if architecture changed)

Component added/removed/replaced = canvas update via `json-canvas` skill. Renames, refactors, features within existing components = no canvas touch. This rule exists to limit JSON-edit breakage and Syncthing conflicts.

### 6. Confirm

One-line summary to user: what was written where.

## /checkpoint resume <name>

1. Read `02 Projects/<name>/STATE.md` and the Decisions log + Gaps sections of `<name>.md`.
2. If `## Active playbook` names a plan file, read it from the repo.
3. Report: "Last session: <X>. Done: <...>. Next: <...>. Blockers: <...>. Active playbook: <NN>." Then ask nothing — wait for the user to direct, or proceed with "Next" if the user already said to continue.

## Rules

- Orchestrator sessions only. Model-router workers and build subagents never write the vault.
- Skip the save entirely if the session did no substantial work (reading, Q&A only) — say so instead of writing a noise entry.
- Respect other machines: never delete content sourced from another machine (check `source-machine` footers); merge and update the footer.
- STATE.md under ~40 lines. If it grows past that, prune Done into the project .md's Current state section.
