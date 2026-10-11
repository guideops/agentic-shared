---
name: design-system-guidantstudios
description: Guidant Studios' house visual language - the full robo design system (dot-matrix halftone art, 6 pixel-sprite agents, pixel icons, 36-component gallery, animated backgrounds, particle typography, interactive dot effects, sub-guides for slides, apps, courses, infographics and quick pages) re-skinned to an Adidas-Originals cobalt palette, Archivo + JetBrains Mono type, with ASCII as the signature feature and silver metal as a rationed material. Use whenever the user types /design-system-guidantstudios, or asks for anything "in Guidant Studios style", "in our studio style", "GS style" - pages, decks, apps, infographics, components, posters, social tiles.
---

# /design-system-guidantstudios - The Locked Visual Language

`/design-system-guidantstudios <anything>` = build that thing in this style. It is the **complete robo system** (structure, techniques, assets, agents, components) re-skinned to **Guidant Studios**: Adidas-Originals cobalt on gallery white, sharp Swiss-sport typography, **ASCII as the signature** and **silver metal as a secondary material**. Every rule below is locked: exact values, not inspiration. If something isn't covered, extend it with the existing tokens and assets. Never import a new colour, font, radius or shadow type.

Credit: built on **robo** by RoboNuggets (CC BY 4.0, see `LICENSE`). Liquid-metal engine: metal-fx (MIT) + Paper Shaders (Apache-2.0); the notices are in `assets/metal/`.

**Visual references this was locked from:** the Adidas Originals "unite all originals" lounge (cobalt lowercase type and a logo wall on white), the niti.therapy grid (cobalt organic shapes on off-white with photo greys), the "Take small steps" poster (cobalt checker staircase with heavy ink grotesk), and PACE+ (cobalt, black and brushed silver with extended uppercase type and line-art product outlines).

**This file is the BASELINE.** Palette, type, spacing, corners, shadows, components, the dot-matrix technique, ASCII and metal below apply to **every** build. Then read the one file that matches what you're making:

| Building... | Read | Covers |
|---|---|---|
| **Quick / throwaway HTML** (summary, one-pager, comparison) | **`lite.md`** | self-contained tokens; read ONLY that file. Triggered by "lite", "quick", "throwaway" |
| Slides, decks, presentations | **`slides.md`** | layout, scroll-snap, arrow-key nav, motion extension |
| Apps, tools, dashboards, web UI | **`apps.md`** | dark/light toggle, app-shell patterns |
| Course / curriculum landing pages | **`courses.md`** | volume + module spine, per-volume pegs (cobalt/ink/silver ramp only) |
| **Infographic / one-pager visual** to screenshot | **`infographic.md`** | pixel icons, varied agents with A1 as the cobalt lead, dot-matrix texture |
| **Animated background** behind any build | **`backgrounds.md`** | 11 dot-matrix backgrounds, plus the 3 ASCII backgrounds in "ASCII layer" below |
| **ASCII art, ASCII agents, frames, scramble, photo to ASCII** | the **"ASCII layer"** section below + `references/ascii-lab.html` | the signature feature |
| **Silver / foil / chrome surfaces** | the **"Metal material"** section below | rationed secondary material |
| Dot-matrix from a **photo** or **animated subject** | "Dot-matrix from a source" | `references/dot-source-image.html`, `references/dot-source-scene.html` |
| **Interactive text / dot effects** | "Particle typography", "Interactive dot effects" | `references/particle-text.html`, `references/interactive-effects.html` |

## The asset kit (all in this folder - copy before hand-building)

| Path | What |
|---|---|
| `brand-book.html` | **Open FIRST.** The style documenting itself: palette, type ramp, panels, ASCII, metal, agents, marks, components, the NOT list. Match it |
| `assets/starter.html` | Full page template: tokens, fonts, favicon, theme toggle, ASCII + metal scripts wired |
| `assets/ascii/gs-ascii.js` | The ASCII engine: `field`, `fromImage`, `agent`, `box`, `rule`, `scramble`, `bg` + data-attribute auto-init |
| `assets/metal/dsx-metal.js` | WebGL liquid-silver frame (`data-metal`). Licences alongside |
| `components/gallery.html` + `components/01-36` | 36 self-contained components: robo's 32 re-skinned, plus 33 ASCII hero, 34 ASCII frame card, 35 foil panel, 36 cobalt poster panel |
| **Agents** - the 6 pixel sprites A1-A6 | `AGENTS` object below, `references/dot-agents-bob.html` (bob), `components/21-agent-row.html`, `components/30-leaderboard.html`, ASCII twins via `GSAscii.agent()` |
| `references/ascii-lab.html` | Live ASCII lab: recipe twins, photo to ASCII converter (txt/png export), agents, frames, rules, scramble, backgrounds |
| `references/dot-system-book.html` | robo's dot-matrix brand book re-skinned: principles, shape recipes, card + icon spec, layout rules |
| `references/dot-backgrounds.html`, `dot-source-image.html`, `dot-source-scene.html`, `dot-shading.html`, `dot-objects.html`, `particle-text.html`, `interactive-effects.html` | robo's engines, re-skinned |

**Improving this style:** update `SKILL.md`, `brand-book.html` and the affected component together.

---

## Marks

**Default mark: the Pixel G** (placeholder studio mark until an official logo is supplied). It's a 7x7 pixel "G", flat `currentColor`. Inline it verbatim:

```html
<svg class="mark" viewBox="0 0 56 56" aria-label="Guidant Studios" style="width:40px;height:40px;color:var(--accent)"><path d="M8 0h8v8h-8zM16 0h8v8h-8zM24 0h8v8h-8zM32 0h8v8h-8zM40 0h8v8h-8zM0 8h8v8h-8zM0 16h8v8h-8zM0 24h8v8h-8zM24 24h8v8h-8zM32 24h8v8h-8zM40 24h8v8h-8zM48 24h8v8h-8zM0 32h8v8h-8zM48 32h8v8h-8zM0 40h8v8h-8zM48 40h8v8h-8zM8 48h8v8h-8zM16 48h8v8h-8zM24 48h8v8h-8zM32 48h8v8h-8zM40 48h8v8h-8z" fill="currentColor"/></svg>
```

**Wordmark:** `guidant studios`, all lowercase, Archivo 700, `letter-spacing:-0.04em`, set in `--accent`. This is the Adidas "unite all originals" voice. It never goes uppercase, expanded, Doto or mono.

**Oval lockup** (from PACE+): the wordmark inside an outlined ellipse, `border:1.5px solid currentColor; border-radius:50%; padding:6px 18px`. Use it once per view at most, for badges, closers and stickers.

**Logo wall** (from the Adidas lounge): Pixel G repeated on a 48px grid, cobalt on white, at full strength. It is allowed **only** as one full-bleed brand-moment section per page, with no other content on it.

**Not ours:** robo's faceted gem, cube hexagon and nugget logo belong to RoboNuggets. Never use them as marks. The hexagon as a plain *shape* (hex recipe, honeycomb background) is fine.

## Defaults (apply unless told otherwise)

- **Light first.** The page is gallery white `#f6f6f3`. Dark mode exists through the toggle (`gs-theme` localStorage key). Ink sections and cobalt panels provide the contrast beats.
- **One signature moment per section: ASCII or metal, never both.** ASCII leads (hero art, agent lineups, frames, scramble labels). Metal supports (one foil object or frame).
- **Use the agents.** The 6 pixel sprites, varied across a build. A1 is the lead and the one in `--accent`. They bob.
- **Cards follow the card spec.** Hard ink slab, hover lift, hot card in cobalt.
- **Cobalt buttons always take white text.**
- **Favicon ALWAYS.** The Pixel G on a cobalt tile (in the starter block).
- **Line-art scenes** for anything concrete you're asked to "visualize". **Dot-matrix** for abstract, data and texture. **ASCII** for the signature moment.

---

## Colours (LOCKED)

| Token | Light (default) | Dark | Used for - and nothing else |
|---|---|---|---|
| `--bg` | `#f6f6f3` gallery white | `#0b0b0f` ink | Page background |
| `--surface` | `#ffffff` | `#15161b` | Cards, panels, inputs, secondary buttons |
| `--surface-2` | `#ececea` | `#1e2026` | Nested surfaces, table header row, code blocks, row hover |
| `--line` | `#d7d8dc` | `#2a2c33` | 1px dividers, table rules, dark-mode borders |
| `--text` | `#0b0b0f` | `#f2f3f5` | All headings and body text, pixel icons, non-lead agents, dot fields |
| `--muted` | `#5d6069` (5.8:1) | `#9a9ea8` (7.3:1) | Kickers, captions, labels, placeholders |
| `--accent` | `#1433d6` **Originals Cobalt** | `#6f86ff` (lifted cobalt; plain cobalt is only 2.3:1 on ink) | THE one highlight: primary button, recommended option, active state, focus ring, Doto emphasis word, A1, the hot card, key stat |
| `--on-accent` | `#ffffff` (8.5:1) | `#0b0b0f` (6.1:1) | Text and icons on an accent fill |
| `--slab` | `#0b0b0f` | `#2a2c33` | Hard offset shadows (pure black disappears on ink) |

**Fixed values (not themed):**

| Token | Value | Use |
|---|---|---|
| `--cobalt` | `#1433d6` | Cobalt panel fill (full-bleed poster sections, in both modes). Cobalt measured from the references: Adidas wall, niti, PACE+, poster |
| `--on-cobalt` | `#ffffff` | Everything on a cobalt panel: type, line-art strokes, dots, ASCII, the Pixel G |
| `--ink` | `#0b0b0f` | Ink sections inside a light page (PACE+ black panels) |
| `--silver-hi` / `--silver` / `--silver-lo` | `#f2f4f7` / `#c5cad2` / `#8a909a` | **Metal material only** (the `.foil` recipe). Never text, never an accent, never a flat fill on a button |

**Cobalt discipline.** Cobalt appears in exactly two ways:
1. **Highlight.** One deliberate thing per view: the one to pick, click or look at. If nothing needs highlighting, nothing is cobalt.
2. **Panel.** A full-bleed cobalt section with everything on it white. Use at most one cobalt panel per three sections (one per three slides). Nothing inside a cobalt panel is cobalt-highlighted; white is the highlight there.

Never use cobalt for decoration, variety, borders "for colour", or alternating rows.

**Shading-source exception:** the dot-matrix reference engines (`references/dot-objects.html`, `dot-shading.html`, `dot-source-*.html`) draw tonal cobalt/grey gradients into hidden buffers as *light-and-shade input*. Those tints only drive dot size and never appear as flat UI colour. Everything visible stays on the tables above.

**No other colours.** There's no second blue (no navy, sky, cyan or teal), no purple, no status rainbow. Show success or error with text plus a pixel icon in `--text`, or with the accent if it's the one that matters. Chart series are `--text` and `--muted`, with the highlighted series in `--accent`.

**Dots / ASCII on canvas:** light bg uses ink `rgba(11,11,15,.88)`. Dark bg uses off-white `rgba(242,243,245,.85)`. On a cobalt panel, use white `rgba(255,255,255,.9)` for the feature and `.35` for the field. The feature layer is `--accent`. Canvas code reads `--accent` / `--text` at draw time (`getComputedStyle`) and redraws on theme flip. Never hard-code them in JS.

## Typography (LOCKED)

Three families, each with one job. Archivo has a width axis: **only widths 100 (normal) and 125 (expanded) are allowed.**

| Font | Weights | Job |
|---|---|---|
| **Archivo** (wdth 100) | 400, 600, 700 | Everything you read: headings, body, UI, nav, card titles, the wordmark |
| **Archivo Expanded** (`font-stretch:125%`) | 600, 800 | **UPPERCASE ONLY**: marquee words (800), kickers, buttons, tags (600). The PACE+ voice |
| **JetBrains Mono** | 400, 500, 700 | ASCII art (400), terminal + code (400, prompts 700), data labels, meta, timestamps, table numerics (500) |
| **Doto** | 900 | Big stats and numbers, the flip-dot ticker, and **1-2 emphasis words** inside an Archivo heading (in `--accent`). Never body, labels, buttons or nav |

**Type scale** (px; `clamp` for display sizes):

| Role | Font | Size | Weight | Letter-spacing | Line-height |
|---|---|---|---|---|---|
| Marquee (1-3 words, one per view) | Archivo 125, UPPERCASE | `clamp(56px, 10vw, 160px)` | 800 | -0.01em | 0.9 |
| Display / h1 (sentence or lowercase) | Archivo | `clamp(44px, 7vw, 96px)` | 700 | -0.04em | 0.95 |
| h2 | Archivo | `clamp(30px, 4vw, 48px)` | 700 | -0.03em | 1.02 |
| h3 | Archivo | 20px | 600 | -0.01em | 1.3 |
| Lead | Archivo, `--muted` | 19px | 400 | 0 | 1.55 |
| Body | Archivo | 16px | 400 | 0 | 1.6 |
| Small / caption | Archivo | 14px | 400 | 0 | 1.5 |
| Kicker (eyebrow) | Archivo 125, UPPERCASE | 11px | 600 | 0.18em | 1.2 |
| Button | Archivo 125, UPPERCASE | 13px | 600 | 0.08em | 1 |
| Tag / chip | JetBrains Mono, UPPERCASE | 11px | 500 | 0.04em | 1 |
| Data label / meta | JetBrains Mono | 12px | 500 | 0 | 1.4 |
| Code / terminal | JetBrains Mono | 13.5px | 400 (prompt 700) | 0 | 1.6 |
| ASCII art | JetBrains Mono | 8-14px | 400 | 0 | **1.0** (cells must be square-ish) |
| Big stat | Doto | 40-72px | 900 | 1px | 1 |

**Rules:**
- **One display voice per heading block:** a Doto emphasis word, OR a marquee, OR a scrambled mono word. Never two.
- **Doto spacing (topline):** `.doto { margin: 0 0.18em; }`. Its glyphs sit tight on both edges.
- Headings are sentence case or all lowercase (Adidas). **Uppercase is reserved for Archivo Expanded.**
- Body copy max width `68ch`. Never justify text.

Import block:
```html
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..800&family=JetBrains+Mono:wght@400;500;700&family=Doto:wght@900&display=swap" rel="stylesheet">
```

## Spacing (LOCKED)

4px base. Only these values: **4, 8, 12, 16, 24, 32, 48, 64, 96, 128**.

| Use | Value |
|---|---|
| Inline gaps (icon to text, tag padding-y) | 4-8px |
| Related items (form fields, button rows) | 12-16px |
| Card padding | 24px (compact: 16px 20px) |
| Grid gap between cards | 24px |
| Heading to its content | 16px |
| Between blocks inside a section | 48px |
| Section padding (vertical) | 96px desktop / 64px mobile |
| Page side gutter | 32px desktop / 20px mobile |
| Content max-width | 1200px (text-only pages 760px) |

## Corners (LOCKED) - sharp, sport-catalogue edges

| Element | Radius |
|---|---|
| Buttons, inputs, cards, panels, modals, dropdowns | **4px** |
| Tags, chips, tooltips, inline code | **2px** |
| Full-bleed panels (cobalt, ink, foil hero), images, posters, the checker grid | **0** |
| Status dots, avatars, toggle knobs, round icon buttons, the oval lockup | **50%** (only these) |

No pill buttons. Nothing above 4px except the 50% list.

## Shadows (LOCKED) - hard slabs, zero blur, always down-right

| State | Light | Dark |
|---|---|---|
| Card rest | `6px 6px 0 #0b0b0f` | `6px 6px 0 #2a2c33` |
| Card hover | `9px 9px 0` same colour, plus `translate(-2px,-4px)` | same |
| Hot card | `6px 6px 0 var(--accent)`, hover `9px 9px 0 var(--accent)` | same |
| Button rest | none | none |
| Button hover | `4px 4px 0 var(--slab)` + `translate(-2px,-2px)` | same |
| Button active | shadow 0 + `translate(1px,1px)`, `.06s` | same |
| Input focus | `4px 4px 0 var(--accent)`, **faded in** from transparent over `.3s` | same |
| Card on a cobalt panel | `6px 6px 0 #0b0b0f` | same |

Transitions: transform/box-shadow `.15s ease` for buttons and `.18s ease` for cards. Nothing slower than `.3s` except page-load fades and the ASCII scramble (`.9s`).

## Buttons (LOCKED)

- **Primary:** `--accent` fill + 2px `--accent` border, `--on-accent` text. Archivo Expanded 600, 13px, UPPERCASE, `0.08em`. Padding `14px 24px`, min-height 44px, radius 4px. An optional trailing `→` or `+` glyph slides 4px on hover. **One per view.**
- **Secondary:** `--surface` fill, 2px `--text` border (dark mode: `--line`), `--text` text.
- **Ghost / link:** no fill or border, `--text`. On hover it turns `--accent` and the `→` slides 4px.
- **ASCII button** (technical contexts: terminals, dev tools, agent consoles): JetBrains Mono 500, 13px, lowercase, rendered `[ run agent ]`, no border or fill. On hover the brackets turn `--accent` and the label scrambles once.
- **On a cobalt panel:** primary flips to a `#ffffff` fill with `#1433d6` text. Secondary is a transparent fill with a 2px white border and white text.
- **Physics:** flat at rest, lifts with a hard slab on hover, collapses on press (Shadows table).
- **Focus-visible:** `outline: 2px solid var(--accent); outline-offset: 3px`.
- Metal never goes on a text button. A **round icon button** (play, send, arrow) may take `data-metal="circle"`, and that counts as the view's metal.

## Cards (LOCKED)

Radius 4px. Light: `#ffffff` surface, 2px `#0b0b0f` frame, `6px 6px 0 #0b0b0f` slab. Dark: `#15161b` surface, 1px `#2a2c33` border, `#2a2c33` slab. Interactions are identical in both modes.

```css
.card { background:var(--surface); border:2px solid var(--text); border-radius:4px; padding:24px;
        box-shadow:6px 6px 0 var(--slab); transition:transform .18s ease, box-shadow .18s ease; }
.card:hover { transform:translate(-2px,-4px); box-shadow:9px 9px 0 var(--slab); }
.card.hot { border-color:var(--accent); box-shadow:6px 6px 0 var(--accent); }
.card.hot:hover { box-shadow:9px 9px 0 var(--accent); }
.card.hot .card-title { color:var(--accent); }
html[data-theme="dark"] .card { border:1px solid var(--line); }
```

**Anatomy:** pixel icon (40-44px, nudges `translateY(-3px) rotate(-8deg)` on hover) or an ASCII glyph → kicker (Archivo Expanded) → title (Archivo 600, 21px, -0.01em) → body (14px, `--muted`) → optional ghost link. Max one hot card per group. Cards enter with a staggered fade-up.

**ASCII frame card** (`components/34-ascii-frame.html`): a box-drawn frame (`┌─┐`) in JetBrains Mono replaces the CSS border. Use it for logs, specs, agent status and terminal-adjacent content. It has no slab shadow; the frame is the depth.

**Inputs:** radius 4px, 2px `--text` border in light / 1px `--line` in dark. On focus the border turns `--accent` and the accent slab fades in. `::selection { background:var(--accent); color:var(--on-accent); }` on every build.

## Panels + compositions (from the references)

| Pattern | Spec | Source |
|---|---|---|
| **Cobalt panel** | full-bleed `#1433d6`, everything white, radius 0. Hosts a marquee, line-art outline or ASCII in white | PACE+ blue posters |
| **Ink panel** | full-bleed `#0b0b0f` inside a light page, `#f2f3f5` text, cobalt-lifted `#6f86ff` accent | PACE+ black panels |
| **Checker step** | cobalt/white hard-stop checker (`conic-gradient` with hard stops, 120px cells) cut as a staircase, heavy Archivo 700 ink type stepping down it | "Take small steps" poster |
| **Repeat stack** | one marquee word repeated 4-6x, tight `line-height:.85`, cropped by the panel edge, last line cobalt or overlapped by an outline object | PACE+ |
| **Lowercase statement** | 2-3 line lowercase Archivo 700 heading in cobalt on white, nothing else | Adidas "unite all originals" |
| **Organic blob** | one smooth cobalt blob shape (SVG path) as the single visual on off-white | niti.therapy |

These are layout recipes, not extra colours. They obey every token above. `components/36-cobalt-panel.html` has the cobalt panel, repeat stack and checker step.

---

## ASCII layer - the signature feature (LOCKED)

ASCII is what makes this system ours: monospace characters as an image medium, crisp and technical. It is the AI-studio counterpart to the Adidas sport-catalogue type. **Engine:** `assets/ascii/gs-ascii.js` (window `GSAscii`). **Live lab:** `references/ascii-lab.html`.

| Element | How | Use it for |
|---|---|---|
| **ASCII field** | `GSAscii.field(pre, {cols, rows, fn, fn2})` with any halftone recipe function | hero art, section art. **Every dot recipe has an ASCII twin**: sphere, hex, wave, bars, sunburst |
| **ASCII from image** | `GSAscii.fromImage(pre, img, {cols:100})` | portraits, product shots, photos as type |
| **ASCII agents** | `<pre data-ascii-agent="a1">` → solid `██` blocks | agent lineups in terminals and docs. **Solid blocks only**, never a ramp or halftone agent |
| **Box frames** | `GSAscii.box(lines, {style:'single', title})` | frame cards, spec sheets, receipts, logs |
| **Rules** | `<div class="ascii-rule" data-ascii-rule="+-">` | section dividers. Patterns: `+-`, `─`, `═`, `· `, `▚` |
| **Scramble** | `<span class="mono" data-ascii-scramble>studios</span>` | one kicker or hero mono word per section, on scroll-in (`="hover"` replays on hover) |
| **ASCII backgrounds** | `<canvas data-ascii-bg="swell|drift|rain">` | hero / landing background. Counts as **the** one animated effect on the page |

**Character ramp (locked):** `' .:-=+*#%@'` (light → dense). Block ramp `' ░▒▓█'` is for block-art and agents only. Never invent other ramps.

**ASCII CSS (in the starter):**
```css
.ascii { font:400 10px/1 'JetBrains Mono',monospace; letter-spacing:0; white-space:pre; color:var(--text); margin:0; }
.ascii .ascii-hot { color:var(--accent); font-weight:400; }
.ascii-rule { font:400 12px/1 'JetBrains Mono',monospace; color:var(--muted); white-space:nowrap; overflow:hidden; width:0; min-width:100%; } /* width:0 trick: never widens its grid/flex parent */
.mono { font-family:'JetBrains Mono',monospace; }
```

**Rules:**
- ASCII is always JetBrains Mono, `line-height:1`, `letter-spacing:0`, `white-space:pre`. Any other line-height breaks the image.
- Colour follows the dot rules: ink on light, off-white on dark, white on cobalt, with `--accent` for the one feature layer (`fn2`, wrapped in `.ascii-hot`) only.
- **Size for round shapes:** `rows = round(cols × 0.6 × boxH / boxW)`. Default hero field is 96 × 40 at 10px.
- **Text over ASCII:** the field behind text drops to 20% opacity, or the brightness function leaves a hollow zone where the text sits. The same rule applies to dots.
- Static ASCII art is deterministic: use `pn()`, never `Math.random()`. Only animated backgrounds and scramble may randomise.
- **Max one scramble per section.** Scramble only fixed-width text (mono or Doto spans) so the layout never jitters.
- ASCII is an **image medium**. It is never used to set body copy, buttons or headlines. Headlines stay Archivo; no figlet banner fonts.
- An ASCII background, a dot background, particle text and interactive dot effects all share **one animation lane: one per page.**

## Metal material - secondary, rationed (LOCKED)

Silver reads futuristic next to cobalt (the PACE+ bag, bottle and foil). It is a **material for surfaces and objects, never paint for text or buttons**. Two forms:

**1. Foil surface (CSS, static): `.foil` / `.foil.crumple`.** A brushed-silver panel with a light sweep on hover. `.crumple` adds a crumpled-foil relief, an SVG turbulence and diffuse-lighting texture blended in. Use it for one hero object tile, a featured stat block, a product or merch mock, or a "coming soon" panel. Text on foil is `#0b0b0f`, or `#1433d6` at 24px+.

```css
.foil { position:relative; overflow:hidden; color:#0b0b0f;
  background:
    linear-gradient(115deg, transparent 30%, rgba(255,255,255,.6) 46%, transparent 62%) -160% 0/250% 100% no-repeat,
    repeating-linear-gradient(90deg, rgba(255,255,255,.08) 0 1px, rgba(0,0,0,.035) 1px 3px),
    linear-gradient(180deg, #f2f4f7 0%, #c5cad2 42%, #8a909a 64%, #dfe3e8 100%);
  transition:background-position .9s ease; }
.foil:hover { background-position:160% 0, 0 0, 0 0; }
```
(The `.crumple` texture data-URI is in `assets/starter.html` and `components/35-foil-panel.html`.)

**2. Liquid-silver frame (WebGL): `data-metal`** via `assets/metal/dsx-metal.js` (a real-time liquid-metal ring with a cool halo). Allowed on **one** of: the hero media frame, a featured image tile, or a round icon button (`data-metal="circle"`). Load `dsx-metal.js` at the end of `<body>`; inline it in single-file deliverables (about 240 KB). It falls back automatically (`html.dsx-metal-off`) on missing WebGL2 or reduced motion. The page must read complete without it.

**Rules:**
- **Max one metal element per view** (foil OR frame), and never in the same section as an ASCII signature element.
- Never metal text, chrome headlines, metal buttons with labels, metal cards in a grid, metal inputs or tables. `dsx-metal-text.js` stays unused in this system.
- Silver tokens (`--silver-*`) live only inside the foil recipe.

---

## Agents + pixel icons (LOCKED - from robo, kept intact)

The 6 agent sprites A1-A6 are the team. 8 rows × 4 columns, mirrored to 8 wide:

```js
const AGENTS={
 a1:[[0,0,1,0],[1,1,1,1],[1,1,1,1],[1,0,1,1],[1,1,1,1],[1,1,1,1],[1,0,0,1],[0,0,0,0]],
 a2:[[0,0,1,0],[0,1,1,1],[1,1,1,1],[0,1,0,1],[0,1,1,1],[1,1,1,0],[0,0,1,0],[0,0,0,0]],
 a3:[[0,0,1,0],[0,0,1,1],[0,1,1,1],[0,1,0,1],[0,1,1,1],[1,1,1,1],[1,0,1,0],[0,0,0,0]],
 a4:[[1,0,0,0],[1,1,0,0],[0,1,1,1],[0,1,1,1],[1,1,0,1],[0,1,1,1],[0,1,0,1],[0,0,0,0]],
 a5:[[0,0,1,0],[0,0,1,1],[0,1,1,1],[1,1,0,1],[1,1,1,1],[1,1,1,1],[1,0,0,1],[0,0,0,0]],
 a6:[[0,0,1,1],[0,1,1,1],[1,1,1,1],[1,1,0,1],[1,1,1,1],[0,1,1,1],[0,0,1,1],[0,0,0,0]]
};
function agSvg(key,ox,oy,c,cls='ag'){ const d=AGENTS[key]||AGENTS.a1; let s=`<g class="${cls}" stroke="none" shape-rendering="crispEdges">`;
  for(let y=0;y<8;y++) for(let x=0;x<4;x++){ if(d[y][x]){
    s+=`<rect x="${ox+x*c}" y="${oy+y*c}" width="${c}" height="${c}"/>`;
    s+=`<rect x="${ox+(7-x)*c}" y="${oy+y*c}" width="${c}" height="${c}"/>`; } } return s+'</g>'; }
```

- **Colours:** non-lead agents are `--text`. **A1 is the lead, in `--accent`**. The accent moves to whichever agent a view highlights. On a cobalt panel all agents are white. Never other hues.
- **Always solid** pixel sprites (SVG rects, canvas cells, or ASCII `██` blocks). Never dot-matrix, halftone or ramp-shaded agents.
- **They bob by default:** the whole sprite hops `0%,100% translateY(0); 15% translateY(-0.6px); 30% translateY(0)` over 1.2s ease-in-out infinite, staggered `0.2s × index`, with a ground-shadow ellipse that squashes in time (`opacity .12→.06`, `scaleX 1→.7`). Only agents bob; marks stay static. Demo: `references/dot-agents-bob.html`.
- Vary them across a build; don't use A1 everywhere.

**Pixel icons:** 10×10 or 12×12 row-string grids on canvas via `sprite()`, one colour per icon (`--text`, `--accent` only for the hot card's icon). Hollow outline style. `image-rendering:pixelated`. Never vector icon sets.

```js
function sprite(canvasId, rows, palette, px) {
  const c = document.getElementById(canvasId); if (!c) return;
  const ctx = c.getContext('2d'); c.width = rows[0].length * px; c.height = rows.length * px;
  ctx.clearRect(0, 0, c.width, c.height);
  rows.forEach((row, y) => [...row].forEach((k, x) => { if (k !== '.') { ctx.fillStyle = palette[k]; ctx.fillRect(x * px, y * px, px, px); } }));
}
```

## Visuals - dot-matrix halftone (the base technique, from robo)

Every abstract or data visual is a **variable-thickness dot matrix**: dots on a fixed grid whose radius comes from a brightness function. Render on `<canvas>` with this engine (copy verbatim):

```js
function halftone(id, w, h, step, maxR, color, fn, color2, fn2) {
  const c = document.getElementById(id); if (!c) return;
  const ctx = c.getContext('2d'); const dpr = window.devicePixelRatio || 1;
  c.width = w * dpr; c.height = h * dpr; c.style.width = w + 'px'; c.style.height = h + 'px'; ctx.scale(dpr, dpr);
  for (let y = step / 2; y < h; y += step) for (let x = step / 2; x < w; x += step) {
    const u = x / w, v = y / h;
    let b = fn(u, v), col = color;
    if (fn2) { const b2 = fn2(u, v); if (b2 > b) { b = b2; col = color2; } }
    if (b <= 0.02) continue;
    ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, Math.min(maxR, b * maxR), 0, Math.PI * 2); ctx.fill();
  }
}
function pn(x, y) { const v = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return v - Math.floor(v); }
function inPoly(pts, u, v) { let s = false; for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) if ((pts[i][1] > v) !== (pts[j][1] > v) && u < (pts[j][0] - pts[i][0]) * (v - pts[i][1]) / (pts[j][1] - pts[i][1]) + pts[i][0]) s = !s; return s; }
```

- **Small dots by default:** `step` ≈ 6px, `maxR` ≈ 0.3 × step. Go up to 0.45 × step only for a deliberate hero subject.
- **Illustrations must be shaded:** dot size varies to show form (lambert light, or 3-tone quantised faces). Flat fills are for icons and diagrams only. The benchmarks are `references/dot-shading.html` and `references/dot-objects.html`.
- Two layers max: an ink/off-white field plus one cobalt feature layer (`fn2`). Use `pn()`, never `Math.random()`, in static renders.
- **Recipe library:** sphere (lambert), hexagon (`inPoly`), arrow, bar chart, wave, sunburst (hollow centre for type), mountain, hourglass, vortex, cube, lightning. A new shape is a new 10-30 line brightness function. Never hand-place dots. **Banned shape: ring/orbit.**
- Source-sampled dots (photo, animated scene), particle typography and the 5 interactive dot effects (torch reveal, flow field, agent constellation, elastic grid, shape morph) are unchanged from robo. They're documented in `references/` and in `backgrounds.md`, with physics constants tuned. Change them only with a reason.

## Line-art scenes (from robo)

Use these for anything concrete you're asked to "visualize": a desk, a product, a climb. Flat stroked SVG: `stroke-width:2.4; stroke-linecap:round; stroke-linejoin:round`. Solid objects are filled with the section's own bg. The one highlight is `--accent`. **On a cobalt panel all strokes are white** (the PACE+ tube outline). Agents live inside scenes. Colour through CSS classes, never `var()` in SVG attributes (it doesn't resolve). Give inline SVGs an `aspect-ratio` or they collapse to 0 height in flex columns. Never mix line-art and dot-matrix inside one illustration.

## Gotchas (learned the hard way in robo)

1. `inset:0` does not stretch a canvas. Set `width:100%; height:100%` explicitly.
2. Declare `color-scheme` (`html{color-scheme:light}` + `html[data-theme="dark"]{color-scheme:dark}`) or Chrome's Auto Dark inverts the palette.
3. A duplicate `const` name kills the entire script silently. Headless-verify that JS-built visuals render.
4. Wait for `document.fonts.ready` before sampling text or drawing ASCII on canvas, or you get fallback-font glyphs.
5. Arrows/connectors never sit at absolute coordinates over HTML. They share an SVG/canvas coordinate system, take their own grid cell, or are measured at runtime.

---

## Starter block (copy-paste - every build starts here)

Put this in `<head>`. The full page template with theme toggle, ASCII and metal wired is `assets/starter.html`.

```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#1433d6">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='8' fill='%231433d6'/%3E%3Cpath d='M17 11h6v6h-6zM23 11h6v6h-6zM29 11h6v6h-6zM35 11h6v6h-6zM41 11h6v6h-6zM11 17h6v6h-6zM11 23h6v6h-6zM11 29h6v6h-6zM29 29h6v6h-6zM35 29h6v6h-6zM41 29h6v6h-6zM47 29h6v6h-6zM11 35h6v6h-6zM47 35h6v6h-6zM11 41h6v6h-6zM47 41h6v6h-6zM17 47h6v6h-6zM23 47h6v6h-6zM29 47h6v6h-6zM35 47h6v6h-6zM41 47h6v6h-6z' fill='%23fff'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..800&family=JetBrains+Mono:wght@400;500;700&family=Doto:wght@900&display=swap" rel="stylesheet">
<style>
:root, html[data-theme="light"] {
  --bg:#f6f6f3; --surface:#ffffff; --surface-2:#ececea; --line:#d7d8dc;
  --text:#0b0b0f; --muted:#5d6069; --accent:#1433d6; --on-accent:#ffffff; --slab:#0b0b0f;
  --cobalt:#1433d6; --on-cobalt:#ffffff; --ink:#0b0b0f;
  --silver-hi:#f2f4f7; --silver:#c5cad2; --silver-lo:#8a909a;
  color-scheme:light;
}
html[data-theme="dark"] {
  --bg:#0b0b0f; --surface:#15161b; --surface-2:#1e2026; --line:#2a2c33;
  --text:#f2f3f5; --muted:#9a9ea8; --accent:#6f86ff; --on-accent:#0b0b0f; --slab:#2a2c33;
  color-scheme:dark;
}
*,*::before,*::after { box-sizing:border-box; margin:0; padding:0; }
body { background:var(--bg); color:var(--text); font:400 16px/1.6 'Archivo',system-ui,sans-serif; -webkit-font-smoothing:antialiased; }
::selection { background:var(--accent); color:var(--on-accent); }
.wrap { max-width:1200px; margin:0 auto; padding:0 32px; }
section { padding:96px 0; }
h1 { font-weight:700; font-size:clamp(44px,7vw,96px); letter-spacing:-.04em; line-height:.95; }
h2 { font-weight:700; font-size:clamp(30px,4vw,48px); letter-spacing:-.03em; line-height:1.02; margin-bottom:16px; }
h3 { font-weight:600; font-size:20px; letter-spacing:-.01em; line-height:1.3; }
p { max-width:68ch; }
.lead { font-size:19px; line-height:1.55; color:var(--muted); }
.kicker, .xp { font-stretch:125%; font-weight:600; text-transform:uppercase; }
.kicker { font-size:11px; letter-spacing:.18em; color:var(--muted); margin-bottom:12px; display:block; }
.marquee { font-stretch:125%; font-weight:800; text-transform:uppercase; font-size:clamp(56px,10vw,160px); letter-spacing:-.01em; line-height:.9; }
.doto { font-family:'Doto',monospace; font-weight:900; color:var(--accent); margin:0 .18em; }
.stat { font-family:'Doto',monospace; font-weight:900; font-size:56px; letter-spacing:1px; line-height:1; }
.mono { font-family:'JetBrains Mono',ui-monospace,monospace; }
.wordmark { font-weight:700; letter-spacing:-.04em; text-transform:lowercase; color:var(--accent); }
.btn { display:inline-flex; align-items:center; gap:8px; min-height:44px; padding:14px 24px; border-radius:4px;
  font:600 13px/1 'Archivo',sans-serif; font-stretch:125%; letter-spacing:.08em; text-transform:uppercase; text-decoration:none; cursor:pointer;
  background:var(--surface); color:var(--text); border:2px solid var(--text); transition:transform .15s ease, box-shadow .15s ease; }
html[data-theme="dark"] .btn { border-color:var(--line); }
.btn:hover { transform:translate(-2px,-2px); box-shadow:4px 4px 0 var(--slab); }
.btn:active { transform:translate(1px,1px); box-shadow:none; transition-duration:.06s; }
.btn:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }
.btn-primary { background:var(--accent); border-color:var(--accent) !important; color:var(--on-accent); }
.btn .arr { transition:transform .15s ease; } .btn:hover .arr { transform:translateX(4px); }
.card { background:var(--surface); border:2px solid var(--text); border-radius:4px; padding:24px;
  box-shadow:6px 6px 0 var(--slab); transition:transform .18s ease, box-shadow .18s ease; }
html[data-theme="dark"] .card { border:1px solid var(--line); }
.card:hover { transform:translate(-2px,-4px); box-shadow:9px 9px 0 var(--slab); }
.card.hot { border-color:var(--accent); box-shadow:6px 6px 0 var(--accent); }
.card.hot:hover { box-shadow:9px 9px 0 var(--accent); }
.card.hot .card-title { color:var(--accent); }
.card-title { font-size:21px; font-weight:600; letter-spacing:-.01em; margin-bottom:8px; }
.card-body { font-size:14px; line-height:1.55; color:var(--muted); }
.tag { display:inline-block; border:1.5px solid currentColor; border-radius:2px; padding:4px 8px;
  font:500 11px/1 'JetBrains Mono',monospace; letter-spacing:.04em; text-transform:uppercase; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:24px; }
.panel-cobalt { background:var(--cobalt); color:var(--on-cobalt); --text:#ffffff; --muted:rgba(255,255,255,.78); --accent:#ffffff; --on-accent:#1433d6; --slab:#0b0b0f; }
.panel-ink { background:var(--ink); color:#f2f3f5; --text:#f2f3f5; --muted:#9a9ea8; --accent:#6f86ff; --on-accent:#0b0b0f; --surface:#15161b; --line:#2a2c33; --slab:#2a2c33; }
.ascii { font:400 10px/1 'JetBrains Mono',monospace; letter-spacing:0; white-space:pre; color:var(--text); margin:0; }
.ascii .ascii-hot { color:var(--accent); font-weight:400; }
.ascii-rule { font:400 12px/1 'JetBrains Mono',monospace; color:var(--muted); white-space:nowrap; overflow:hidden; width:0; min-width:100%; } /* width:0 trick: never widens its grid/flex parent */
.foil { position:relative; overflow:hidden; color:#0b0b0f;
  background:linear-gradient(115deg,transparent 30%,rgba(255,255,255,.6) 46%,transparent 62%) -160% 0/250% 100% no-repeat,
    repeating-linear-gradient(90deg,rgba(255,255,255,.08) 0 1px,rgba(0,0,0,.035) 1px 3px),
    linear-gradient(180deg,#f2f4f7 0%,#c5cad2 42%,#8a909a 64%,#dfe3e8 100%);
  transition:background-position .9s ease; }
.foil:hover { background-position:160% 0,0 0,0 0; }
@media (max-width:640px){ .wrap{padding:0 20px;} section{padding:64px 0;} }
@media (prefers-reduced-motion:reduce){ *{transition:none!important;animation:none!important;} }
</style>
```

Set `<html lang="en" data-theme="light">`. At the end of `<body>`: inline `assets/ascii/gs-ascii.js` (always), and `assets/metal/dsx-metal.js` only if the page uses `data-metal`.

---

## What this style is NOT

Never use any of these. If a request seems to need one, solve it with the tokens and assets above.

**Fonts - never:**
- Outfit (that's robo / design-system-x), Inter, Roboto, Arial, Helvetica, SF Pro, Open Sans, Poppins, Montserrat, Lato, DM Sans, Space Grotesk, Manrope, Syne, Unbounded, Clash, Satoshi, or a system default as the visible font
- Any serif (Playfair, Georgia, Source Serif) or script
- Courier, Courier New, Consolas, Fira Code, Space Mono or `monospace` fallback as the visible mono. Mono is JetBrains Mono only
- Archivo at widths other than 100 / 125, Archivo weights 100-300 or 900, or Archivo Expanded in lowercase or for body copy
- Doto for body, labels, buttons, nav or whole headlines
- Figlet / banner ASCII fonts for headlines, and uppercase normal-width headlines (uppercase belongs to Archivo Expanded)

**Colours - never:**
- Any hex not in the Colours tables (no "slightly different blue", no "slightly different grey")
- A second blue: navy, royal, sky, baby, cyan, teal, electric or neon blue. **One cobalt `#1433d6`** (+ its dark-mode lift `#6f86ff`)
- Purple, violet, indigo, or any blue-to-purple "AI gradient"
- Robo's palette: orange `#ff6b1a`, yellow `#f5a623`, cream `#e8e2d2`, paper `#f2efe8`, warm ink `#1c1a16`
- design-system-x's silver accent `#c8d2dd` as a highlight. Silver here is material only
- Red/green/amber status fills, rainbow charts, multi-colour tag sets
- Gradients, except the foil recipe, the metal-fx layer and hard-stop patterns (checker). No gradient text, no gradient buttons, no mesh gradients
- Pure `#000000` page backgrounds (ink is `#0b0b0f`), pure `#ffffff` text in dark mode (`#f2f3f5`). White on a cobalt panel is correct
- Cobalt used for decoration; more than one hot card per group; more than one cobalt panel per three sections

**Effects - never:**
- Blurred, soft or glowing shadows, neon outlines, coloured glows. The only blur-like effect is the metal-fx halo
- Glassmorphism, `backdrop-filter`, translucent frosted cards
- Pill buttons, radii above 4px (except the 50% list), mixed radii on one element type
- ASCII and metal in the same section; more than one metal element per view
- Metal or chrome on text, labelled buttons, inputs, tables or card grids
- Matrix-green rain, CRT scanlines, RGB-split glitch, VHS noise, typewriter effects on body copy
- ASCII set in a non-mono font, ASCII with `line-height` ≠ 1, ASCII used for paragraphs or buttons
- Dotted, halftone or ramp-shaded agents (agents are always solid); the ring/orbit shape
- More than one animated background/effect per page (dot or ASCII); full-strength dots or ASCII behind text
- RoboNuggets marks (faceted gem, cube hexagon, nugget logo); emoji as icons; vector icon fonts (Lucide, Heroicons, Font Awesome)
- Stock photography, 3D clay renders, isometric SaaS illustrations, AI-generated "futuristic" imagery with glows
- Paragraph walls, bullet walls, hex-mesh backgrounds, random agent scatter, watermarks, corner slide numbers

## Pre-flight checklist (run before delivering)

1. Cobalt is `#1433d6` in light and `#6f86ff` in dark, with white text on cobalt fills. No other blue anywhere (grep the hex).
2. The font import is Archivo + JetBrains Mono + Doto only. Widths are 100/125, weights are within the Typography table, and uppercase appears only in Archivo Expanded.
3. Every colour maps to the Colours tables.
4. Shadows are zero-blur slabs. Radii are 0, 2px, 4px or 50%.
5. One primary button, at most one hot card per group, A1 is the only accent agent, and agents bob.
6. Each section has at most one signature (ASCII or metal). At most one animated effect per page. Dots and ASCII behind text are at 20%.
7. ASCII is JetBrains Mono at line-height 1, the ramp is `' .:-=+*#%@'`, and static art is deterministic.
8. Spacing is on the 4px scale. The Pixel G favicon is present. `data-theme` and `color-scheme` are set. Canvas art reads CSS vars and redraws on theme flip.
9. Headless-render in both themes before calling it done (`--use-angle=swiftshader` if metal is used).
