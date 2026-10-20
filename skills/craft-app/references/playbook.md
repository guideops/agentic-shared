# CRAFT micro-app playbook

Run in order. Every block is copy-paste ready; swap the [bracketed] parts. Distilled from the RoboNuggets RUBRIC kits (Scripts, Teleprompter, Docs, Generations) and the CRAFT build guide.

## 0 · Frame it (before any prompt)

1. **One job.** "A small app where I ___ so my agent can ___." If it needs "and", it is two kits.
2. **Who writes what.** List the files and mark each one agent-written, app-written, or both. Both means `rev`.
3. **The loop.** How does the person hand work back (comments, a hand-off box, picks), and what does `apply` do?
4. **Out of scope.** Two things it will not do.

## C1 · The build

```
build me a small local app called [NAME]. it [ONE JOB].
- [what I see first, in plain words]
- [what I can do there: pick / edit / comment / drag]
- [the detail view, if any]
it has no AI inside: it shows data/[content].json, which my agent writes, and saves my work to data/state.json.
node only, no npm install, plain html/css/js, one server.mjs on localhost:[PORT].
drop in sample content so every button works straight away. make it look like a real finished app, not a rough draft.
```

## C2 · The design

```
now make it look like my brand instead of generic. use my design system:
- [background] with a faint dotted texture, [text colour], one [accent] as the only accent, used only for the one thing to click
- [heading font] and [body font], small uppercase tracked labels
- cards with a 2px frame and a hard offset shadow that slides in on hover, lots of breathing room
- dark mode first with a light toggle, remembered on this computer
- every colour as a token in one block at the top of the css
make it feel premium and intentional, like proper designer software.
```

## R · The contract

```
now make it agent-proof:
- a check.mjs that validates data/*.json, prints OK or one PROBLEM line per issue naming the item and field, and exits 1
- the server tidies a slightly odd file instead of crashing and shows each fix in a yellow line
- saves send the rev they saw; a stale save gets a 409 with the newer data and the page says so
- security: 127.0.0.1 only, refuse writes from other origins, no CORS, serve only public/, 1 MB cap, escape all text
- write skills/[name]/SKILL.md: a YOUR DEFAULTS block, universal rules with the reason in [brackets],
  workflows (open the app, write content, apply my hand-back) where every step ends "Done when ...",
  and a drop-in JSON example. put exact file shapes in references/data.md.
- a README for my agent: setup steps in order with a health check, then use / make it yours / how it's built / security / troubleshooting.
```

For a hosted app with paid services (the RENDER Studio shape), add roles: "[Thinker] does all the thinking, [Designer] makes the images, [Publisher] posts them. keep my keys in the background, never on the page. wire up every button so it runs for real."

## A · The /goal audit

```
/goal
Ask: test [NAME] for real, end to end, in a real browser.
Goal: don't stop until every view and button works by clicking like a person: [list the flows]. also: write the data file
from disk while the page is open and prove the stale-save guard works; check 375px wide with no sideways scroll; check
both themes; node check.mjs prints OK after every agent write. if something breaks, fix it and say exactly what broke.
Examples: the bar is a calm, finished tool like [reference]. don't copy it, beat it.
Negations: don't fake a result. don't test by calling the API directly instead of the UI. no console errors.
don't leave test data behind; restore the sample.
Tools: a real browser with screenshots. end with one short report: what passed, what broke, what you fixed.
```

The five parts work for any hand-off to an agent: **Ask** (the thing and the budget), **Goal** ("don't stop until" plus the observable finish line), **Examples** (the quality bar, "don't copy it, beat it"), **Negations** (hard no's), **Tools** (what to use, how to verify, "don't ask unless truly blocked").

## F · Fire up

```
make it run for real: start it with pm2 (or a terminal), check /api/health, install the skill with its App folder set
to the full path, and give me the link. if it goes inside [shell: Agentic Workspace / Scaffold], add it as a page using
the same pattern as [existing page], with the data folder pointed at [synced folder].
```

Hosted for a client: "put this online on [host], locked behind a simple username and password, keys as server env vars, never in the code. then double-check it works for the client start to finish."

## T · Tailor

```
this is my template now. restyle it for [client / theme] by changing only the token block in app.css and the YOUR
DEFAULTS block in the skill. pull [site] for colours, fonts and logo. don't touch how it works underneath.
```

## Definition of done

- [ ] Runs with `node server.mjs` on a clean machine, no install step
- [ ] Sample data on first open; every control clickable
- [ ] `check.mjs` passes; the skill's write workflows end on it
- [ ] A malformed data file shows a yellow banner, not a crash, and is never overwritten
- [ ] An agent write during an open session triggers the stale-save message; nothing lost
- [ ] Loopback only, Origin check, path jail, body cap, escaping
- [ ] 375px with no sideways scroll; dark and light both legible; keyboard shortcuts for the main moves
- [ ] README sections: Set it up · Use it · Make it yours · How it's built · Security model · If something looks wrong
- [ ] Copy has no long dashes and no jargon; every error names its fix
