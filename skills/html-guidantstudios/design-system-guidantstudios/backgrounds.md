# /design-system-guidantstudios - Animated Dot-Matrix Backgrounds

A library of **11 reusable animated dot-matrix backgrounds** for /design-system-guidantstudios builds - hero sections,
landing pages, decks, app shells. Each is a full-screen `<canvas>` that sits *behind* content.
They follow the /design-system-guidantstudios Motion Extension rules (grid fixed, time drives dot radius, slow sine loops).

**Live gallery (open FIRST):** `references/dot-backgrounds.html` - all 11, full-screen, with sample
text on top so you can see each as a real background. Scroll / arrow keys to step through. Lift the
function + the engine straight out of this file.

Built 2026-06-29. The original FLOW wave came from a course-page hero;
this library generalises it into named, swappable backgrounds.

## The 11 backgrounds

| # | Name | Placement | Motion | Theme | Function |
|---|------|-----------|--------|-------|----------|
| 1 | **SWELL** | bottom | rolling ocean swell + cobalt pulse on the crest | paper | `fSwell` (+`fSwellHot`) |
| 2 | **RAIN** | top → down | falling matrix streaks per column | paper | `fRain` |
| 3 | **SCANLINE** | diagonal | a bright band scans corner to corner | paper | `fScan` (+`fScanHot`) |
| 4 | **TIDE** | left edge | left wall breathes wider + narrower | paper | `fTide` |
| 5 | **GATEWAY** | both sides | twin columns pulse, open centre | paper | `fGate` |
| 6 | **MOIRÉ** | full bleed | two grids interfere + drift | paper | `fMoire` |
| 7 | **COMET** | top streak | a head + trail crosses the top | black | `fComet` (+`fCometHot`) |
| 8 | **HONEYCOMB** | full bleed | hexagon mesh, a cobalt wave sweeps through | paper | `fHex` (+`fHexHot`) |
| 9 | **TILES** | full bleed | square grid, tiles light up in a diagonal sweep | black | `fTiles` (+`fTilesHot`) |
| 10 | **SPRITE MARCH** | bottom | the sprite set bobs across, A1 in cobalt | paper | `drawMarch` (custom) |
| 11 | **MORPH MARK** | centre | one mark morphs square → hexagon → circle, looping | black | `fMorph` (+`fMorphHot`) |

(A 12th, BUBBLES / pulsing circles, was cut - the circle one was dropped.)

## How they work

Every background is a brightness function `fn(u, v, t, asp)` sampled on a fixed dot grid. `u,v` are
0..1 across the screen, `t` is seconds, `asp = W/H` (use it for shapes that must stay round - hex,
morph). The function returns 0..1 → the dot's radius. **The grid never moves; only radius/colour
change over time.** An optional `fn2` paints the cobalt accent layer on top.

`SPRITE MARCH` is the one exception - a `custom(ctx, W, H, t)` draw that stamps the agent sprites
(from `SIDEBAR_ICON_DATA`) as dots and bobs them.

### Performance (locked best practice)

A single `requestAnimationFrame` loop + an `IntersectionObserver` so **only the on-screen background
animates** - the others sit idle. That's how 11 full-screen canvases stay smooth in one file. Source:
MDN Optimizing-canvas, Treehouse rAF. Keep loops 6-10s and sine-eased so any paused frame still looks
like a finished static /design-system-guidantstudios frame.

## How to use one in a build

1. Add the canvas + CSS: `<canvas id="dotBg"></canvas>` with
   `position:fixed; inset:0; width:100vw; height:100vh; z-index:0; pointer-events:none;` and put your
   content in a `z-index:1` wrapper.
2. Copy the `halftone`/`makeBg` engine + the one `fn` (and its `fn2`) you want from
   `references/dot-backgrounds.html`.
3. Drive it: `const draw = makeBg(canvas, def); requestAnimationFrame(t => draw(t/1000));` (or wire the
   IntersectionObserver pattern if the page has several).
4. Palette stays /design-system-guidantstudios: ink dots `rgba(11,11,15,a)` on paper, off-white `rgba(242,243,245,a)` on black,
   cobalt `#1433d6` for the one accent. Keep base alpha ~0.4-0.5 so text stays readable on top.

Pick by mood: bottom anchors (SWELL, SPRITE MARCH), edges (TIDE, GATEWAY), full-bleed texture
(MOIRÉ, HONEYCOMB, TILES), motion accents (COMET, SCANLINE), centre focal (MORPH MARK).

All baseline rules still apply (`DESIGN-SYSTEM.md`): two layers max, `pn()` not `Math.random()`, banned
ring/orbit shape, text-over-dots opacity rule if any text sits directly on the canvas.

## The 3 ASCII backgrounds (Guidant Studios signature)

Character-grid twins of the dot backgrounds, from `assets/ascii/gs-ascii.js`. Drop-in, zero config:

```html
<canvas data-ascii-bg="swell" data-ascii-strength=".3" style="position:absolute;left:0;bottom:0;width:100%;height:70%"></canvas>
```

| Mode | Motion | Use |
|---|---|---|
| `swell` | a rolling crest of ramp characters (` .:-=+*#%@`) along the bottom, cobalt flecks ~5% | hero / cover - the default |
| `drift` | slow interference field across the whole canvas | calm section background behind sparse content |
| `rain` | restrained falling glyph columns in ink (never green) | agent / terminal / "processing" moments |

Rules: same lane as every other animated effect - **one per page**. `strength` = max field alpha (default `.3`; keep text-over-ASCII legible - lower to `.2` behind body copy). Only-animates-when-visible and `prefers-reduced-motion` (static frame) are built in. Colours come from `--text` / `--accent`, so theme flips are automatic.
