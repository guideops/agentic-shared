---
name: project-kickoff
description: Start a new project with vault documentation - decision log (ADR), architecture canvas, and STATE.md resume note in Obsidian. Trigger /project-kickoff <name>, or "kickoff project", "start new project docs". Also supports adopt mode for existing projects.
---

# Project Kickoff

Creates the single-source-of-truth documentation for a new project in the Obsidian vault, following the `02 Projects/` convention established 2026-07-20.

## Vault location (per-machine resolution, in order)

1. `$CLAUDE_VAULT` env var, if set — the preferred per-machine override.
2. Known paths: `C:\Users\pawar\Documents\ajqcd-zaozt` (Windows Desktop), `~/Documents/ajqcd-zaozt`, `~/ajqcd-zaozt`, `~/vault/ajqcd-zaozt`.
3. Windows only: `%APPDATA%\obsidian\obsidian.json` → vault whose folder name is `ajqcd-zaozt`.
4. Nothing found → **no-vault machine.** Tell the user this skill requires the Obsidian vault (or `CLAUDE_VAULT` set) and stop — do NOT scaffold vault files in a guessed location.

Project folder: `<vault>/02 Projects/<Project Name>/`

## Modes

- `/project-kickoff <name>` — new project, full flow below.
- `/project-kickoff adopt <name>` — existing project folder: add missing `STATE.md` only. Do NOT regenerate or overwrite the existing `.md` or `.canvas`.

## Flow (new project)

### 1. Gather decisions

Interview the user (AskUserQuestion, batched — max 2 rounds) for anything not already stated:
- What is it, one sentence. Who is it for.
- Stack decisions: framework, database, hosting, auth, styling. For EACH: which options were considered and WHY the winner won. Decisions without rationale are not accepted — if the user says "Next.js", ask "over what, and why".
- Constraints: budget, existing infra to reuse (check `05 Agent/Infrastructure - Machine Sync Overview.md` and Projects Index for reusable patterns — e.g. PokieTicker two-layer AI cost model, INSTRUMENT design system, AURA daemon).
- Model strategy for the build: which models plan vs build (see SOP-04 Model Selection in `05 Agent/SOPs/`).

### 2. Create `<Name>.md`

Structure (matches existing project docs — see `02 Projects/Agentic Workspace/Agentic Workspace.md` as reference):

```markdown
---
title: <Name>
status: active
updated: <today>
source-machine: <machine>
tags: [project]
---

# <Name>

## What it is
## Why it exists
## Current state (as known on <machine>, <date>)
## Architecture (plain English)
## Decisions log
## Gaps and risks
## Roadmap / what's left
## Open questions
```

**Decisions log format (ADR-style)** — one entry per decision:

```markdown
### D-001 — <title> (<date>)
- **Chosen:** <option>
- **Rejected:** <option A> (<one-line reason>), <option B> (<reason>)
- **Why:** <2-3 sentences of real rationale>
- **Revisit if:** <condition that would invalidate this>
```

Use mermaid blocks inside this file for flows/sequences (data flow, auth flow). Mermaid lives in the .md, NOT the canvas.

### 3. Create `<Name>.canvas`

Use the `json-canvas` skill. Architecture map only — coarse:
- One node per component (frontend, backend, DB, external services)
- Labeled edges for relationships
- Stack-choice nodes reference their ADR id (e.g. "Next.js — see D-001")
- Keep under ~15 nodes. Detail belongs in the .md.

### 4. Create `STATE.md`

```markdown
---
title: <Name> — State
updated: <today>
source-machine: <machine>
---

# State

## Last session
<date> — kickoff. Docs created.

## Done
- Project documentation created

## Next
- <first concrete build step>

## Blockers
- none

## Active playbook
- none yet (see SOP-02 for feature-build flow)
```

### 5. Update Projects Index

Append the project to `02 Projects/Projects Index.md` following its existing format. Do not restructure the index.

### 6. Repo pointer (if a repo exists or is being scaffolded)

Add to the repo's `CLAUDE.md`:

```markdown
# Documentation source of truth
Project docs, decisions (ADR log), and session state live in the Obsidian vault:
`02 Projects/<Name>/` (synced via Syncthing).
- Update via /checkpoint at session end.
- Feature specs live in this repo under plans/ as numbered playbooks (see SOP-02).
- Model-router workers: NEVER write to the vault. Orchestrator sessions only.
```

## Rules

- Vault writes happen ONLY in orchestrator sessions (never delegate vault writes to model-router workers or subagents on other models).
- Never overwrite an existing project folder — if it exists, switch to adopt mode and tell the user.
- Every decision entry MUST have a rejected-alternatives line and a why. Refuse to log "chose X" without rationale.
- Footer every file: `*Knowledge source: <machine>, <date>. Merge — don't duplicate — when updating from another machine.*`
