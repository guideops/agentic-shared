# Kit anatomy

The shape every RUBRIC-style kit shares. The template at `rubric-planner/` is a working instance; copy from it.

```
<kit>/
├── README.md                 written for the agent first (setup steps in order), plain English for the person
├── LICENSE                   keep upstream credit when adapting a RoboNuggets kit (CC BY 4.0)
├── app/
│   ├── server.mjs            CONFIG block · tolerant loader · GET /api/data · POST save (rev) · GET /api/health
│   ├── check.mjs             OK, or "PROBLEM <item>: <field> ..." per issue, exit 1; --server also pings health
│   ├── data/                 sample content on first run; the only state; back this up and you backed up everything
│   └── public/
│       ├── index.html        (+ one detail page if the job needs it, routed like /s/<id>)
│       ├── app.js | common.js   theme, Store (load, save with rev, stale reload on 409), escape, helpers, copy-for-agent text
│       ├── app.css           one :root token block, dark + light under html[data-theme]
│       └── icon.svg
└── skills/<name>/
    ├── SKILL.md              YOUR DEFAULTS · universal rules [reason] · workflows with "Done when" · drop-in JSON
    └── references/data.md    exact file shapes · what the app tidies · saving and the stale tab
```

## Server essentials

- `const PORT = Number(process.argv[2] || process.env.<KIT>_PORT) || 500xx;` and `const DATA = path.resolve(process.env.<KIT>_DATA || path.join(HERE, 'data'));`
- Loader: parse, normalise every record to known fields only, give duplicates a suffix, push a human sentence per fix into `problems`. A file that is not JSON at all: return empty data plus a problem, and refuse saves (`broken`) so it is never overwritten.
- Save: `if (Number(inp.rev) !== Number(cur.rev)) return 409 { stale: true, rev, <data> }`, else write `rev + 1` to `file.tmp`, then `renameSync`.
- Guards: `listen(PORT, '127.0.0.1')`; on POST, if an `Origin` header is present it must equal `http://` + `Host`; `path.normalize(path.join(PUBLIC, p)).startsWith(PUBLIC + path.sep)`; body capped at 1e6; `Cache-Control: no-store` on API responses; `X-Content-Type-Options: nosniff`.
- Port in use: catch `EADDRINUSE` and print "It may already be running: open http://localhost:<port>, or run node server.mjs 4000".

## Page essentials

- Render through one `render()` from the store. Never save layout scratch onto data objects (put it in a Map); the planner audit caught exactly this leak.
- Re-render must not eat typing: skip a redraw while a note is focused, and restore a half-typed input's value and focus.
- Reload from disk on window focus only when nothing is dirty and nobody is typing (that is how agent writes appear).
- Prefix state classes (`is-top`, `is-done`) so they never collide with layout classes (`.top` header). Another real audit bug.
- Keyboard: single-letter shortcuts ignored inside inputs; `Esc` closes the top layer; shortcuts shown on `kbd` chips.
- Hand-back: a "Copy for agent" text that starts with a fixed heading (`# <KIT> comments` / `# <KIT> brief`), carries ids in braces, and ends with the `apply` command, so the skill can trigger on the paste.

## Skill essentials

- Description lists the trigger phrases, including the paste heading.
- YOUR DEFAULTS holds the app folder (full path at install), address, and every tunable number.
- Rules carry their reason in [brackets]: the agent follows a rule it understands, and an edge case gets judged by the reason.
- Every workflow step ends with "Done when ...". Write workflows end with running `check.mjs` until OK.
