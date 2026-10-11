---
name: html-guidantstudios
description: Produce HTML output instead of markdown, in the Guidant Studios visual language. Four levels - Static Doc, Visual Artifact, Two-Way Interactive, Throwaway Tool - based on Thariq Shihipar's "Unreasonable Effectiveness of HTML" framework. Every file is built in design-system-guidantstudios (Originals cobalt, Archivo + JetBrains Mono, ASCII signature, rationed silver metal, robo agents and dot-matrix). Explicit invocation only - "/html-guidantstudios", "html guidant studios", "gs html", "html this in studio style".
---

# /html-guidantstudios - HTML output in the Guidant Studios style

**Explicit-invocation only.** Do not use this skill unless the user says `/html-guidantstudios`, "html guidant studios", "gs html", or asks for an html artifact "in Guidant Studios / studio style". Without one of those, respond normally (plain `/html` stays with the original `html` skill). When invoked, and the task is a doc, plan, report, review, design, prototype, dashboard, or editor - make it HTML instead of markdown. Higher information density, easier to read, easier to share, and (at levels 3-4) interactive.

This skill encodes the four levels of HTML output, the patterns that work at each level, and the rules that keep agent-generated HTML from looking AI-slop.

**Every file is built in design-system-guidantstudios - no exceptions.** The full system ships inside this skill at `design-system-guidantstudios/` (the complete robo system re-skinned to Guidant Studios). At the start of every build read `design-system-guidantstudios/DESIGN-SYSTEM.md`; start from `assets/starter.html`; run its pre-flight checklist before delivering. The level decides *what* you build; the design system decides *how it looks*.

**Use the assets, don't hand-roll.** Before building any piece, check `design-system-guidantstudios/components/gallery.html` (36 components: buttons, cards, stat tiles, tables, nav, hero, callouts, timeline, pricing, charts, form inputs, checklist, agent rows, flip-dot ticker, receipt, heatmap, radar, gauge, ticket, leaderboard, terminal, marquee, plus the 4 studio signatures: ASCII hero, ASCII frame card, foil panel, cobalt panel) and copy from there. Visuals use the house techniques: dot-matrix halftone art, pixel-sprite icons, the six agent sprites (A1 in cobalt, bobbing), line-art scenes, and the Pixel G mark. For decks also read `design-system-guidantstudios/slides.md`; for tools/dashboards `design-system-guidantstudios/apps.md`; for screenshot visuals `design-system-guidantstudios/infographic.md`.

**ASCII is the signature; metal is rationed.** Every html file inlines `design-system-guidantstudios/assets/ascii/gs-ascii.js` before `</body>` and gets at least one ASCII moment: a scrambled mono kicker, an `.ascii-rule` divider, an ASCII field as the hero visual, ASCII agents, or a box-drawn frame for logs/specs. Metal is optional and capped at **one element per view** (a `.foil` panel, or `data-metal` on a hero media frame / round icon button), never in the same section as an ASCII signature, never on text or labelled buttons. Rules: "ASCII layer" and "Metal material" in `design-system-guidantstudios/DESIGN-SYSTEM.md`.

> **Credit:** Framework and use-case taxonomy from **Thariq Shihipar** ([@trq212](https://x.com/trq212)) of the Anthropic Claude Code team. Original article: [Using Claude Code - The Unreasonable Effectiveness of HTML](https://x.com/trq212/status/2052809885763747935). Examples gallery: [thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/). This skill is one community implementation of his ideas - go read the source.

---

## When to reach for HTML over markdown

Markdown's default. HTML wins when **any** of these are true:

- The output is over ~100 lines (markdown stops getting read)
- It needs charts, tables, SVG diagrams, side-by-sides, or spatial layout
- It needs to be shared (HTML is a link; markdown is an attachment)
- The reader will manipulate it (sliders, toggles, drags, picks)
- It synthesises data from multiple sources (filesystem, MCPs, git, browser)
- It will exist for one use and then be thrown away

Markdown stays better for: tiny notes, commit messages, README first-pass, things that need to round-trip through git diffs.

---

## The Four Levels

Each level is a strict superset of the last in capability and effort. Most agent output stops at Level 1. The unlock is recognising when you should be at 3 or 4.

### Level 1 - Static Doc

**HTML as a better markdown.** One-way, read-only. Replaces a long .md file with something readable.

**Use cases:** specs, research reports, explainers, incident write-ups, weekly status, plans, PR write-ups, summaries.

**Defining moves:**
- Headings, sections, intro/TL;DR up top
- Archivo body at 16px / 1.6, 68ch measure; Archivo Expanded kicker above the H1 (scrambled on load via `data-ascii-scramble` on a mono span), one Doto emphasis word in the H1
- Pull-quotes (`.pull`), callouts (`.callout`), footnotes; TL;DR in a `.tldr` card
- Mobile responsive - viewer might open on phone
- Sticky table of contents (`.doc` + `.toc`) for anything > 1500 words

**Example prompt:**
> "Create a thorough implementation plan as an HTML file. Headers, TL;DR at top, key code snippets inline, sticky TOC on the left. Easy to digest."

### Level 2 - Visual Artifact

**HTML adds visual density.** Still read-only. Information that text can't convey lands here.

**Use cases:** design systems, slide decks, flowcharts, dashboards (snapshot view), comparison tables, SVG illustrations, component galleries, before/after pairs.

**Defining moves:**
- SVG for diagrams and flowcharts (never PNG when SVG works). ASCII is for the signature moment - hero art, agent lineups, box-framed specs/logs - not for diagrams that must be read precisely
- Tables for any comparison or matrix
- Spatial layout - grids, side-by-sides, columns
- Inline charts (`<svg>` bar/line/donut, no charting library), styled with the `.fig` token classes: series in `--text`/`--muted`, the highlighted series in `--accent`
- Emphasis as data - the one thing that matters in `--accent`, everything else in `--text`/`--muted` steps; severity and diff states use labels, glyphs and weight, never extra hues (the system has one cobalt and no red/green/rainbow)
- Slide-deck format with `scroll-snap` for talks (`.deck` + `.slide`); white, ink and cobalt-panel slides (`.panel-ink`, `.panel-cobalt`, max one cobalt per three slides)

**Example prompt:**
> "Read the rate limiter code and produce a single HTML explainer page: a token-bucket SVG flow diagram at the top, 3-4 annotated code snippets, gotchas section at the bottom. Optimised for someone reading it once."

### Level 3 - Two-Way Interactive

**HTML the reader can manipulate.** Sliders, toggles, drags, inline edits. The export pattern is mandatory: every Level 3 artifact ends with a button that turns the manipulated state back into a prompt or structured output the agent can act on.

**Use cases:** design tuning (animations, colours, easing curves), parameter sweeps, A/B option pickers, prompt iteration with live preview, draft review with inline comments, picking values from a range.

**Defining moves:**
- Sliders, toggles, dropdowns, draggable cards - styled with the starter controls; picked options are `.card.pick.hot`
- Live preview that re-renders on input
- **Export button at the end** - `Copy as prompt` / `Copy as JSON` / `Copy as markdown`. Uses `navigator.clipboard.writeText`. Without it the level collapses to a toy.
- **Comment box per item** - every card / option / row / section the reader reviews gets its own `<textarea class="comment">` for notes. Roll those comments into the export output (label each by item) so feedback comes back attached to what it is about. This is the highest-value interactive pattern here - don't skip it.
- State stays in the DOM - no backend. Reload = reset is fine for throwaways.
- Inline edits use `contenteditable` or `<input>` directly on the page

**Example prompt:**
> "I'm tuning this system prompt. Make a side-by-side HTML editor: editable prompt on the left with variable slots highlighted, three sample inputs on the right that re-render the filled template live. Add a character counter and a Copy button."

### Level 4 - Throwaway Tool

**A purpose-built mini-app for one task.** Looks like a real product but exists for this one piece of data. Always ends with an export back to the agent.

**Use cases:** triage boards (drag tickets across columns), feature-flag editors with dependency warnings, dataset curation (approve/reject/tag rows), annotation tools, config editors with validation, prompt-template tuners, file-comparison views, manual data entry with constraints.

**Defining moves:**
- Multi-panel layout (`.toolbar` + `.shell`: sidebar / canvas / inspector)
- Domain-specific UI: kanban columns, file tree, diff view, editable table
- Validation and feedback inline (`.warn`: warnings, errors, dependency hints - accent rule + `[!]` mono prefix + text, no red)
- Keyboard shortcuts where useful
- **Export button is the unlock** - `Copy as markdown` / `Copy diff` / `Copy as JSON`. Without it this is a useless one-off. With it, the reader's manual work becomes the agent's next prompt.
- Throwaway in effort, not in look - still full design-system-guidantstudios. No build step, no framework, single file. Logs and status panes use ASCII frame cards; the run action can be an `[ run ]` `.btn-ascii`.

**Example prompt:**
> "I need to reprioritise these 30 Linear tickets. Make an HTML file with each ticket as a draggable card across Now / Next / Later / Cut columns. Pre-sort by your best guess. Add a 'Copy as markdown' button that exports the final ordering with a one-line rationale per bucket."

---

## Best Practices (scoured from Thariq's 20 examples)

### Design system - design-system-guidantstudios (LOCKED)

This replaces any generic palette or type advice. Full rules live in `design-system-guidantstudios/DESIGN-SYSTEM.md` - read it at the start of every build. The essentials:

**Colours** (light is the default; dark via the toggle):

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#f6f6f3` | `#0b0b0f` | page background |
| `--surface` | `#ffffff` | `#15161b` | cards, panels, inputs, TL;DR, sidebars |
| `--surface-2` | `#ececea` | `#1e2026` | code blocks, callouts, comment boxes, nested surfaces |
| `--line` | `#d7d8dc` | `#2a2c33` | dividers, table rules, section borders, dark-mode borders |
| `--text` | `#0b0b0f` | `#f2f3f5` | headings and body |
| `--muted` | `#5d6069` | `#9a9ea8` | kickers, captions, labels, secondary series |
| `--accent` | `#1433d6` Originals Cobalt | `#4466ff` Studio Cobalt (same hue, lifted for black) | the ONE highlight per view: primary/export button, picked option, active state, focus, Doto word |
| `--on-accent` | `#ffffff` | `#ffffff` | text on accent fills - white in both modes |
| `--slab` | `#0b0b0f` | `#2a2c33` | hard offset shadows |

Dark mode: accent as *text* only at 18px bold / 24px+ (titles, Doto word, stats); smaller accent labels stay `--text`. Never a lavender/periwinkle accent.

Fixed: cobalt panel `#1433d6` with everything `#ffffff`; ink panel `#0b0b0f`; silver `#f2f4f7 / #c5cad2 / #8a909a` inside the `.foil` recipe only.

**Type:** Archivo 700 headings (H1 `clamp(44px,7vw,96px)`, `-0.04em`, sentence case or lowercase), Archivo 600 h3/card titles, Archivo 400 body 16px/1.6. **Archivo Expanded** (`font-stretch:125%`) 600 uppercase for kickers (11px, `.18em`) and buttons (13px, `.08em`); 800 uppercase for a 1-3 word marquee. **JetBrains Mono** for code, table headers and numerics, tags, TOC, summaries, and all ASCII (line-height 1). Doto 900 only for 1-2 emphasis words in a heading or a big stat, with `margin:0 .18em`. No serif, no italic accents, no other mono.

**Spacing:** 4px scale only (4, 8, 12, 16, 24, 32, 48, 64, 96, 128). **Corners:** 4px (buttons, inputs, cards, code blocks), 2px (tags, inline code), 0 (full-bleed panels, images), 50% only for dots/avatars/round icon buttons. **Shadows:** hard offset, zero blur - cards `6px 6px 0 var(--slab)`, hover `9px 9px 0` + lift, hot card in `--accent`. **Surfaces:** flat `--surface` with a 2px ink frame (light) / 1px `--line` (dark) - no sheen gradients. **Buttons:** primary = cobalt fill + white text, secondary = surface + 2px border, ghost = text link with sliding `→`, ASCII = `[ label ]` in mono for technical contexts.

### Studio identity - mandatory per level

Tokens alone make a recoloured generic doc. Every file must also carry the studio's identity pieces. The starter ships with all of them wired up, so keep them unless a rule below says otherwise:

| Piece | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| `.studio-bar` - Pixel G + `guidant studios` wordmark + mono meta + toggle | ✓ | ✓ (decks: on the first slide) | ✓ | ✓ (merge into `.toolbar`) |
| Scrambled mono kicker (`data-ascii-scramble`) above the H1 | ✓ | ✓ | ✓ | ✓ |
| ASCII signature visual (hero field, ASCII twin of the concept, or framed spec) | ✓ (hero) | ✓ (one per section max) | optional | logs/status in ASCII frames |
| `+-` ASCII rule between major sections | ✓ | ✓ | ✓ | panel separators |
| Agents: A1 on the TL;DR; agent sprites wherever people, roles, owners or assignees appear (`agentSvg()`, A1 lead in accent, bobbing) | ✓ | ✓ | ✓ | ✓ (assignee avatars) |
| Pixel icons (`sprite()`) instead of bullets/emoji for feature or category lists | when listing | ✓ | ✓ | ✓ |
| Cobalt panel for the one big statement (max one per three sections/slides) | optional | ✓ for decks | - | - |
| Footer `.studio-foot`: oval wordmark lockup + mono skill/level line | ✓ | ✓ | ✓ | in the status bar |

Before delivering, check it would be recognisably Guidant Studios with the colours removed (greyscale test). If not, it's missing identity pieces.

### Layout

- `.page` wrap: max-width 1200px, `padding: 48px 32px 64px`
- Sections separated by `border-bottom: 1px solid var(--line)` with 48px padding top and bottom (96px for landing-style pages)
- 2-column hero: text left, visual right, collapse to 1-col at 880px
- Visuals: inline SVG with the `.fig` classes for diagrams/charts; an ASCII field (`GSAscii.field`) or the dot-matrix halftone engine for illustration/data-art; one animated background max (`data-ascii-bg` or `design-system-guidantstudios/backgrounds.md`) when a page wants motion
- Section dividers: `<div class="ascii-rule" data-ascii-rule="+-"></div>` between major sections is the default house divider
- For editor patterns (Level 4): sticky `.toolbar`, full-bleed `.shell` canvas, optional inspector panel right

### Interaction patterns (Level 3-4)

**The Export button is the contract.** Every interactive HTML must end with an `.export` bar holding a primary button labelled exactly what it exports (it is the one accent button on the page):

```html
<div class="export"><button id="copyBtn" class="btn btn-primary">Copy as markdown</button><span class="summary" id="summary"></span></div>
```

Standard handler (already wired in `assets/starter.html` - you only write `buildExport()`):

```js
const btn = document.getElementById('copyBtn');
btn.addEventListener('click', () => {
  const md = buildExport();
  navigator.clipboard.writeText(md).then(() => {
    btn.textContent = '✓ Copied';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.textContent = 'Copy as markdown';
      btn.classList.remove('copied');
    }, 2000);
  });
});
```

**Tri-state buttons for review patterns** (blank → approve → reject → blank) - `.tri` button (JetBrains Mono glyphs `·` `✓` `✗`), cycle on click, encode as `data-state` (`approve` = cobalt fill, `reject` = muted strike-through).

**Inline picks** - for "choose A/B/C" UIs, make each option a `.card.pick` that toggles `.hot` on click. Single pick per group (so at most one hot card per group).

### Single-file discipline

- One `.html` file. Inline `<style>` and `<script>` - including the contents of `gs-ascii.js` (~9 KB), and `dsx-metal.js` (~240 KB) only if the page uses `data-metal`. No build step. No external CSS/JS deps except the Google Fonts import (Archivo wdth 100-125 + JetBrains Mono + Doto 900).
- All assets either inline SVG or `data:` URLs. No `/img/foo.png` folders.
- The file is the artifact - you (or the viewer) can email it, drop it in Slack, open it on a phone, archive it.

### Favicon - always

Every build ships the Pixel G favicon from `assets/starter.html` (white pixel G on a `#1433d6` tile) plus `<meta name="theme-color" content="#1433d6">`. Swap in a content-relevant pixel glyph on the same cobalt tile when there is an obvious one (a bar chart for a data page, a coin for money, a bolt for speed), drawn in white.

### Anti-patterns to avoid

The full banned list is "What this style is NOT" in `design-system-guidantstudios/DESIGN-SYSTEM.md`. The ones that bite html builds most:

- Any colour outside the token table: a second blue (navy, sky, cyan), purple or blue-to-purple gradients, severity reds/greens, chart rainbows, design-system-x silver as an accent, robo orange
- Gradients other than the foil recipe and metal-fx; glassmorphism / backdrop blur - in docs *and* tools
- Blurred or glowing shadows (the metal-fx halo is the exception); pill buttons; radii above 4px
- Outfit, Inter, Roboto, Helvetica or system-ui as the visible font; serif or italic display type; Courier or system monospace instead of JetBrains Mono; uppercase normal-width headings
- ASCII and metal in the same section; more than one metal element per view; metal on text or labelled buttons
- ASCII art for diagrams that must be read precisely; matrix-green rain, scanlines, glitch effects; ASCII with line-height other than 1
- Icon libraries and emoji icons - use pixel-sprite icons (`sprite()` in `design-system-guidantstudios/DESIGN-SYSTEM.md`) or skip icons
- Loading spinners (this isn't a web app, it's a doc) - if something must load, scramble a mono label
- "Generated by AI on {date}" footers
- UI transitions longer than .18s (the .3s input-focus fade, .25s theme switch and .9s ASCII scramble are the only exceptions)

---

## Recipes

### Recipe - Interactive Review (Level 3)

For triaging N options visually with comments + status + clipboard export. Great for reviewing copy variations, media picks, design options.

**Anatomy:**
1. Topline seed block - show original input verbatim
2. Table or grid, one row per item
3. Variation cards per row (`.card.pick`, click toggles `.hot`, single per row)
4. Tri-state status button (`.tri`: blank → ✓ → ✗ → blank)
5. Comments textarea per row (`.comment`)
6. Optional secondary pickers (style, tag, mode)
7. Live summary line at bottom (accumulates picks)
8. **Export bar** (`.export`) - builds structured directive prompt, copies to clipboard

### Recipe - Session Recap (Level 1)

Render the current conversation as a clean static doc. Original `/html` use case.

**Sections:**
1. **Intent** - what the user was trying to do (1 sentence)
2. **Key turns** - prompts + replies that mattered, skip throat-clearing
3. **Decisions** - explicit picks
4. **Artifacts** - file paths created/edited, clickable
5. **Open threads** - anything unresolved

**Save location:** your output folder, as `{YYYY-MM-DD_HHMM}_{slug}.html`. If you keep per-project folders, save it with the project.

### Recipe - Comparison Explainer (Level 2)

For "X vs Y" lessons (Markdown vs HTML, before vs after). Side-by-side panels, inline SVG of the key concept, callout cards.

**Anatomy:**
- Kicker + H1 (Doto emphasis on the pivot word); optional ASCII twin of the concept as the hero visual
- `.tldr` card with the verdict
- Two panes side by side, full width on mobile
- Inline SVG of the mechanism if applicable
- Closing "When to use which" matrix

---

## How to invoke

### In your agent

- You say `/html-guidantstudios`, "html guidant studios", "gs html", or "build me an html for X in studio style"
- The agent picks the level (1-4) based on the task
- Reads `design-system-guidantstudios/DESIGN-SYSTEM.md`, starts from `assets/starter.html`, generates a single `.html` file in the Guidant Studios look, saves it to your output folder, opens it in the browser
- Confirms the path back to you

### Related skills

- **`tweak`** - Inject a live tweak panel into any HTML file (5 or 10 sliders), bake selected values back into source CSS. Pairs with Level 3/4 outputs from `html-guidantstudios`. Available at [github.com/robonuggets/skills](https://github.com/robonuggets/skills).

---

## Rules

- **Only run when explicitly invoked** (see top of file). Never switch a normal answer to HTML on your own.
- **design-system-guidantstudios, always.** Start from `assets/starter.html` with the foundation block untouched, use only its tokens, inline `gs-ascii.js`, and run the pre-flight checklist in `design-system-guidantstudios/DESIGN-SYSTEM.md` before delivering.
- **Pick a level explicitly** at the top of the response: "Using html Level 3 (Two-Way Interactive)".
- **One file. Always.** Inline CSS, inline JS, inline SVG. No asset folder. No build step.
- **Mobile responsive by default.** Test at 360px and 1200px, in both light and dark themes.
- **Export button is mandatory at Level 3+.** Without it, an interactive HTML is a toy.
- **Per-item comment boxes are mandatory at Level 3+.** Each reviewable card/option/section gets its own `<textarea>`, and the comments flow into the export labelled by item.
- **Favicon always.** The Pixel G cobalt tile, never a blank tab.
- **One signature per section.** ASCII or metal, never both; one animated effect per page.
- **Identity pieces present** (studio bar, scrambled kicker, ASCII signature, rules, agents, footer lockup) - see "Studio identity - mandatory per level".
- **Don't summarise away the substance.** If rendering a conversation or doc, preserve actual phrasing of important content.
- **Skip system-reminders, tool-call noise, meta chatter** when extracting source content.
- **Match the level to the task.** A status report doesn't need sliders; a triage board doesn't work without them.
