---
name: personalise
description: Take any external input (tutorial, repo, article, prompt, tool, framework, skill) and recommend how to adapt it to your setup — workspace, work, tech stack, voice, and goals. Triggers on "personalise this", "adapt this for me", "make this fit our setup", "/personalise [thing]".
credits: Adapted from robonuggets/skills (github.com/robonuggets/skills); This setup section localised.
---

# Personalise

You drop something in — a URL, a paste, a file path, a tool name, a workflow, a prompt template. Output: a focused recommendation on how to adapt it to *your* world. Not a generic summary. Not a blind install.

## Process

1. **Classify the input** in one line — skill, tool, article, repo, prompt, workflow, framework, content piece, etc.
2. **Pull only the context you need** — don't read everything:
   - Always skim: the user's goals, mission, and "about me" files (typically the project's main instruction file and any user-profile file)
   - For voice/content inputs: any tone/style/voice file plus relevant content feedback memories
   - For tooling/code inputs: tech stack notes, available tools/services file
   - For placement decisions: workspace structure rules, skill placement rules
   - Always check the memory index for relevant feedback/project entries
   - For overlap detection: grep existing skills and tasks/backlog to spot duplicates
3. **Assess fit** — what's gold for the user, what's mismatched, what's missing, what overlaps with what they already have.
4. **Output the recommendation.**

## Output format

Three sections, tight:

**What this is** — one line.

**Take rate** — `high` / `medium` / `low` / `skip` + one-line reason filtered through the user's stated goals.

**Personalisation plan** — concrete bullets only:
- Where it lives (which workspace / which agent — apply skill placement rules from the project's instructions)
- What to rename (strip upstream branding, match the user's English variant, swap in the user's canonical terms)
- What to drop (anything that conflicts with voice rules, tech stack, or existing feedback memories)
- What to add (links to existing skills/tasks/agents it should reference)
- Prereqs (env vars, packages, tools, infra)
- Approval gates triggered (e.g. paid generation cost approval; messaging-platform replies; external-system actions)

End with one branching question only if there's a real choice. Otherwise stop.

## Lenses to apply

- **Workspace fit** — shared or one specific agent / sub-project? Never duplicate across folders.
- **Naming** — strip personal/upstream names, match the user's English variant (e.g. AU vs US spelling), use their canonical terms.
- **Voice** — apply any voice/tone rules in the project: no AI-smell, no hype, terse, options-first when content involves choices.
- **Tech stack** — match the user's defaults (module system, framework versions, package manager, test runner, linter). Flag mismatches.
- **Goals filter** — does adopting this move the user toward their stated goals? If no, flag low or skip.
- **Existing overlap** — grep first. If overlap, recommend *updating* the existing skill/task instead of creating new.
- **Cost gates** — flag any paid-model usage (image / video / LLM APIs) — needs cost approval before run.
- **External-system gates** — flag if it touches messaging platforms, publishing, git push, or APIs that affect shared state.
- **Memory hygiene** — only propose memory entries if the input is a *preference* or *feedback rule*. Tools, ideas, tutorials don't go in memory.

## What NOT to do

- Don't install/apply without the user's go. Recommend first, execute on confirmation.
- Don't expand scope — one input, one personalisation. No pre-prepping siblings "just in case".
- Don't write planning documents unless asked. Chat output only.
- Don't generate the personalised artifact (rewritten skill, adapted prompt, edited script) until the user picks the take rate and confirms placement.

## This setup — where to look and where things go

Context sources (step 2 above, mapped to this machine):
- **Goals / about-me** — `~/.claude/CLAUDE.md` (global rules), vault `05 Agent/` (SOPs, agent docs)
- **Existing skills** — `~/ai-workspace/claude-projects/agentic-shared/skills/` (shared, canonical) + `~/.claude/skills/` (local-only ones). Grep BOTH for overlap.
- **Memory** — claude-mem: use mem-search / observation_search for past decisions and feedback before recommending
- **Projects / backlog** — vault `02 Projects/<Name>/STATE.md`; workflow roadmap in Workflow System project
- **Tech stack defaults** — per-project CLAUDE.md in each repo

Placement rules (recommendation output):
- Reusable across machines → `agentic-shared/skills/<name>/` + junction into `~/.claude/skills/` (`cmd /c mklink /J` on Windows — plain `ln -s` silently copies in Git Bash) + commit so laptop/VPS sync (SOP-05)
- Machine- or project-specific → local `~/.claude/skills/` or the project repo, no junction
- Workflow rules (not skills) → vault SOPs `05 Agent/SOPs/` — announce full vault path when writing (transparency rule)
- Async/ambient work → route to Hermes lane per SOP-06, not a new skill

Gates to flag (this setup's versions):
- Model cost → SOP-04 Ministry bench rules; delegation must be announced in chat
- External systems → Telegram/Hermes actions, git push, anything publishing
- Credits → adopted external material keeps a `credits:` line in frontmatter (house rule, see calibrate/SOP-02 precedent)
