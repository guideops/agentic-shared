# /design-system-guidantstudios - Course Landing Pages

The /design-system-guidantstudios variant for **course / curriculum landing pages**. Builds on the baseline in `DESIGN-SYSTEM.md` (same palette, type, dot-matrix technique, block cards, pixel icons). This file only adds what's specific to a course page.

## The peg (copy this, don't reinvent)

**Build from one reference page and match it.** Rather than hand-write HTML, drive the page from a generator script.

- **Source of truth = the generator script** (e.g. a small Python `_build_volumes.py`): the HTML is generated; **edit the script, never the HTML**. Copy it for a new course and swap the data.
- **Structure source:** a curriculum checklist (Volumes → topics) in the same folder. The page mirrors the checklist one-to-one.

## Page model

A single scrolling page:
1. **Hero** (header) - see below.
2. **Sticky jump-nav** (`toc-bar`) - one chip per Volume (+ the framework), each in the Volume's accent.
3. **Vertical spine** - Volumes stacked down a dotted spine. Each **Volume** = a numbered node + `VOLUME N` label + descriptive `<h2>` title + one-line purpose + a 3-col grid of **Module** block-cards.
4. Optional **horizontal framework card** can break the spine full-width between two volumes (the peg uses one for "The Agentic Operating System": desk scene + bobbing A1 sprite + 3 bullets).

Hierarchy names: top level = **Volumes** (numbered 1, 2, 3…), the cards inside = **Modules** (numbered continuously across the whole course). A framework card counts as a module in the numbering.

## Hero (locked)

- **Kicker:** the Pixel G mark + the lowercase `guidant studios` wordmark + a one-line tagline in Archivo Expanded uppercase.
- **Bobbing mark:** the A1 agent sprite (cobalt), top-left.
- **Title:** two-line Archivo 700 (`-0.04em`), one word emphasized in Doto cobalt (example: "The *Complete* Masterclass"). Force the break with `<br>` + `white-space:nowrap` so it never wraps to 3 lines.
- **Headshot (right):** circular avatar with an **animated dot-matrix halo** behind it (cobalt dots on a `<canvas>`, ~80% opacity - or an ASCII field halo via `GSAscii.field`, never both), and a small **"by [Name]" tag box** overlapping the lower edge (panel bg, ink border, cobalt offset shadow).
- **Meta bar:** `X volumes · N+ modules · Living curriculum`.

## Cards + art (locked)

- **Block cards:** 3D stacked-depth block cards (the baseline card, with `::before/::after` offset layers). Border + offset shadow in the **Volume's accent**.
- **Every module gets BOTH, and each is UNIQUE across the page:**
  - a **simple pixel-emoji icon** that *relates to the module* (monitor, lock, gear, cloud, plug, target, trophy, money bag…). Keep them simple - pixel-emoji, not busy line art. Authored as 12×12 `#/.` grids → `<rect>`s.
  - a **structured halftone dot pattern** top-right, from clean families (rings / rays / grid / spiral / squares / arcs), generated per-module so no two repeat.
- **Card color flips by theme (locked 2026-06-16):**
  - Light mode: `--card-bg: #ffffff` + ink text (`--card-ink:#0b0b0f`).
  - Dark mode: `--card-bg: #15161b` + off-white text (`--card-ink:#f2f3f5`).
- **Default the page to LIGHT mode** (localStorage choice still wins).

## Per-volume pegs (still one hue)

Volumes need to be told apart on the spine, but this system has **one blue**. So pegs rotate through **tones of the locked palette, not new hues**, in this order:

| Volume | Peg | Card border / slab |
|---|---|---|
| 1, 4, 7 | cobalt `#1433d6` (dark: `#4466ff`) | cobalt |
| 2, 5, 8 | ink `#0b0b0f` (dark: `#f2f3f5`) | ink |
| 3, 6, 9 | silver `#8a909a` (slab) + foil chip on the volume node | silver-lo |

Pair each peg with a different **pattern** on the volume node (solid fill / ASCII `▚` fill / foil) so volumes stay distinguishable without colour. No teal, violet, amber, magenta, cyan, gold or green - ever.

## Build + ship

Two generators (HTML is generated - edit the script, not the HTML):
- **`_build_volumes.py`** - the peg builder. Emits header variants (v1/v2/v3).
- **`_build_course.py`** - the reusable builder. Makes ANY course page from a config. Knobs per course: `accent` (one highlight colour for the whole page), `shades` (a list, one shade per section so each section reads a bit different), photo on/off (off by default now), `hero_agent` (which agent sprite tops the hero), `favicon` (Pixel G tile), `card_label` ("Topic" vs "Module"). It can also parse an existing live page to pull its content.

Steps: point/copy a config, swap the section + card data, run the script, then deploy: copy the built HTML to `index.html` (plus any image) into your deploy folder, then ship it with your host's deploy command.

## Gotchas (learned 2026-06-17)

- **Theme default vs saved choice.** Each page remembers light/dark in a localStorage key (e.g. `course-theme`) plus a `|| 'light'`/`'dark'` fallback. People who visited before keep their saved choice - it wins over the default. To force a new default for everyone, change the KEY name (e.g. bump `course-theme-v1` to `course-theme-v2`). Just flipping the fallback word is not enough for returning visitors.
- **Don't read the file you deploy over.** If the builder parses a live page to get its content, do NOT save the new page over that same file - the next build then reads the new file, finds nothing, and ships a blank page. Keep an untouched copy of the source (e.g. `index-old-live.html`) and parse from that.

Everything else (colors, fonts, dot-matrix engine, canvas gotchas, icon/mark rules) is the baseline in `DESIGN-SYSTEM.md` - read that first.
