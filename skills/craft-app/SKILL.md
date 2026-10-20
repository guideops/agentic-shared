---
name: craft-app
description: Builds a small agent-native micro app the way RoboNuggets builds its RUBRIC kits, following the CRAFT stages (Create, Rig, Audit, Fire Up, Tailor). The app has no AI inside - it is a window on JSON files that the agent writes, with a validator, rev-guarded saves, a security model, an agent-facing README and a skill that drives it. Use when the user says "/craft-app", "craft an app", "build a micro app", "build a kit like Jay's", "CRAFT this", "make a RUBRIC-style app", or wants a small local tool their agent can operate.
argument-hint: "<one-line idea> | stage <C|R|A|F|T> | audit <path> | tailor <path> <brand>"
metadata:
  hermes:
    category: development
---

# CRAFT a micro app

You build a small local app that a person and their agent share. The person sees and decides in the app; the agent thinks and writes files. Build it in the CRAFT order, one stage at a time, and show the person the running app after every stage.

<!-- YOUR DEFAULTS: change these values here, in one place. -->
- Template to copy: the RUBRIC Planner kit, repo `guideops/rubric-planner` (a finished kit built with this skill; reuse its server, check, store and css shapes). Use a local clone when one exists (laptop: `~/ai-workspace/claude-projects/rubric-planner`); otherwise `gh repo clone guideops/rubric-planner` into a scratch folder and copy from there.
- Where new kits go: a new folder beside the other projects on this machine (laptop: `~/ai-workspace/claude-projects/<kit-name>`), each kit its own git repo
- Ports: next free in the 500xx range (50011 Scripts, 50013 Teleprompter, 50015 Planner are taken)
- Design system: RUBRIC tokens (paper `#f2efe8` / dark `#131311`, ink `#1c1a16`, one orange `#ff6b1a`, yellow `#f5a623` secondary, Outfit, 2px frames, hard offset shadow on hover, dark first). For a Guidant-branded kit use /design-system-guidantstudios tokens instead (Tailor stage).
- Shell: Agentic Workspace frames kits as pages (pattern: plan 57 `/scripts`), on the VPS checkout
- Full playbook with copy-paste prompts: `references/playbook.md`. Kit file shapes: `references/kit-anatomy.md`
<!-- END YOUR DEFAULTS -->

## Universal rules

1. **The app has no AI inside.** [Scope stays small, nothing costs money at runtime, the agent can be swapped.] Pages render files and record human decisions. Model calls, research and writing belong to the agent and its skill. Paid API keys live in `.env` for the agent's recipes, never read by the server.
2. **One job.** [The kits are robust because each one does one stage.] If the idea needs "and", propose two kits and build the first. Name two things it will not do, and write them in the README.
3. **Split files by writer.** [Nobody clobbers anybody.] Each data file is agent-written, app-written, or both. A file both write carries `rev`, and every write adds 1.
4. **Build first, brand second.** [A running app with sample content beats a polished mock.] Stage C1 ships working pages with sample data before any styling pass.
5. **Done means proven in a real browser.** [Audit is where the bugs are; the planner build found three.] Never call a stage done from reading code. Click through it, with screenshots.
6. **Plain words everywhere.** [The person reads the README, the errors and the buttons.] Second person, no jargon, every error names its fix, no long dash character.
7. **Ask only what changes the build.** Run /align on a vague idea. Otherwise pick the conventional default and say so.

## Workflow: the five stages

Before C, write the frame in four lines and show it: the one job, the files and who writes each, the hand-back loop (comments, a hand-off box, or picks, and what `apply` does), and the two out-of-scope items. Done when the user agrees or corrects it.

### C · Create
1. **C1 build.** Copy the template's skeleton (`server.mjs`, `check.mjs`, `public/`, `data/`) into the new kit folder, rename everything, then build the pages for this job. Seed `data/` with realistic sample content so every control works. Done when `node server.mjs` serves it and every button does something.
2. **C2 design.** Apply the design system through one token block at the top of `app.css` (dark + light, theme remembered under `robo-theme`). Kicker labels, 2px frames, hard shadow on hover, keyboard shortcuts shown as `kbd` chips. Done when both themes look finished at desktop width.

### R · Rig
1. **Contract.** `check.mjs` validates every data file: it prints `OK` or one `PROBLEM <item>: <field> ...` line per issue and exits 1. It bans the long dash.
2. **Server.** A CONFIG block with env overrides (port, data dir), a tolerant loader that repairs odd files and returns `problems` (shown as a yellow banner), `GET /api/data`, rev-guarded `POST` (409 plus the newer data), `GET /api/health`, atomic tmp-then-rename writes, and the security model: 127.0.0.1, Origin check on POST, no CORS, path jail to `public/`, 1 MB cap, all text escaped.
3. **Skill.** `skills/<name>/SKILL.md`: a YOUR DEFAULTS block, universal rules with the reason in [brackets], workflows (A open the app, B write content, C apply the hand-back, plus any review step) where every step ends "Done when ...", and a drop-in JSON block. Exact file shapes go in `references/data.md`.
4. **README for the agent.** Sections: what's in this package · Set it up (numbered, ending in a health check) · Use it · Make it yours (example change requests) · How it's built (routes table) · Security model · If something looks wrong.
5. **External services** (only if the job needs them): wire them as agent recipes (one `skill/models/<name>.md` per service, like RUBRIC Generations) or, for a hosted app, as server routes with keys in env. Done when `node check.mjs` prints OK on the sample data.

### A · Audit
Run the /goal audit from `references/playbook.md` yourself, in the browser pane. At minimum: every view and control by real clicks and typing, an agent write to the data file while the page is open (the stale guard must fire and nothing may be lost), a malformed file (banner, not a crash), 375px wide with no sideways scroll, both themes, a clean console. Fix what breaks, re-verify it, then restore the sample data. Done when you can list what passed, what broke, and what you fixed.

### F · Fire Up
Local: start the kit (terminal or pm2), check `/api/health`, copy the skill into `~/.claude/skills/<name>` with its App folder set to the full path, and give the link. Inside Agentic Workspace: follow the plan-57 pattern (frame the kit at a route, point the data env var at the vault's `Agentic Output/<name>/`), on the VPS checkout, as its own plan. Hosted for a client: host it, add a login, set keys as server env vars, re-test as the client. Done when the user has a working link.

### T · Tailor
Restyle only through the token block in `app.css` and the skill's YOUR DEFAULTS. For a client, pull their site for colours, fonts and logo. If the kit generates something, change only what the generator is asked to make. Done when the engine files are unchanged (`server.mjs`, `check.mjs` and the data shapes are byte-identical) and the look is new.

## Reporting

After each stage, report in three lines: what is now true, the link, and the next stage. At the end, report the folder, the run command, the skill name, and the Audit findings.
