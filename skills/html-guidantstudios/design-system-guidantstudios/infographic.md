# /design-system-guidantstudios infographic - screenshot-ready infographics

**Trigger:** "gs infographic", "/design-system-guidantstudios infographic", or any /design-system-guidantstudios visual that summarises something you'll **screenshot** (a tweet take, a list, a concept, a breakdown).

**Read this file + the DESIGN-SYSTEM.md baseline** (palette, type, halftone engine, ASCII layer, agents, Pixel G). This file is the recipe; the baseline is the look.

## What an infographic is here
A standalone visual that packs one idea into a screenshot. Not a deck (that's `slides.md`), not a throwaway one-pager (that's `lite.md`, light-mode + no art). Infographics get the full art treatment: pixel icons, agent sprites, the Pixel G, dot-matrix texture, and one ASCII signature element (a field, frame or agent lineup).

## Hard rules (the stuff that bites)

1. **Icons = pixel sprites, NEVER line-art.** Every archetype/concept icon is a pixel grid rendered as crisp SVG rects (see renderer below). Do NOT use stroked line-art SVG scenes for the icons. Line-art scenes are a separate /design-system-guidantstudios language for "visualize a concrete scene" jobs - they are not the infographic icon style. (Locked 2026-06-29 after a build wrongly used line-art; the pixel icon svg rule must hold.)
2. **Default to a normal, scrollable page** you screenshot yourself. Only build a fixed square (viewport-locked, everything must fit) when asked for "square" / "so I can screenshot it as one image". A square that tries to fit 5+ rows + header + footer clips the footer every time - avoid unless asked. (Locked 2026-06-29: default to a normal html page to screenshot.)
3. **Use the agent sprites, vary them, A1 is the cobalt lead.** One sprite per item/card (A2, A3, A4, A5, A6 in ink - off-white on dark), with A1 in cobalt in the header and/or a full lineup. Don't use A1 for everything.
4. **Pixel G + wordmark = the brand mark.** Pixel G (DESIGN-SYSTEM.md "Marks") top-left with the lowercase `guidant studios` wordmark, or the oval lockup in the footer.
5. **Dot-matrix texture on the background** - a faint dot grid (CSS stand-in below, or the canvas halftone for the hero). One ASCII signature element per infographic (hero field, box-framed stat block, or ASCII agent lineup) - never metal and ASCII together.
6. **Cobalt discipline.** Cobalt for: the Pixel G, Doto numbers, the one highlight word, A1. Keep icons in `--text` with at most one cobalt accent pixel-cluster each. Don't flood it. Alternative social format: a full cobalt panel with everything white (no cobalt highlights inside it).

## Palette + type (same as baseline)
- **Light (default):** bg `#f6f6f3`, card `#ffffff`, text `#0b0b0f`, muted `#5d6069`, cobalt `#1433d6`.
- **Dark (if asked, or for a dark social feed):** bg `#0b0b0f`, card `#15161b`, text `#f2f3f5`, muted `#9a9ea8`, accent `#4466ff` (Studio Cobalt - plain cobalt fails contrast on ink), white text on fills.
- **Cobalt panel:** bg `#1433d6`, everything `#ffffff`.
- `html{color-scheme:light}` (or `dark`) so Chrome never inverts it.
- Archivo (headings 700 lowercase/sentence, body 400), kickers in Archivo Expanded 600 uppercase. Doto 900 in the accent for numbers + 1 emphasis word. JetBrains Mono for labels and ASCII. Marquee only for a 1-3 word hero.
- Cards: 2px border (light) / 1px `#2a2c33` (dark), radius 4px, hard zero-blur slab `6px 6px 0`.

## Canonical structure
The "5 archetypes of building now" pattern: header with the A1 lead sprite + Pixel G, 5 cards each with a pixel icon + a different agent sprite + Doto number, dot texture, agent lineup footer. Copy that structure.

## Drop-in renderers (copy verbatim)

```js
// 1) pixel icon: grid of strings, '.'=empty, 'k'=ink (or off-white on dark), 'o'=cobalt accent
const INK='#0b0b0f', COBALT='#1433d6';   // dark mode: INK='#f2f3f5', COBALT='#4466ff'
function pixelSVG(grid, pal){ const n=grid.length,m=grid[0].length; let r='';
  for(let y=0;y<n;y++)for(let x=0;x<m;x++){const ch=grid[y][x]; if(ch==='.')continue;
    r+=`<rect x="${x}" y="${y}" width="1" height="1" fill="${pal[ch]}"/>`;}
  return `<svg viewBox="0 0 ${m} ${n}" shape-rendering="crispEdges">${r}</svg>`; }
// usage: pixelSVG(ICON, {k:INK,o:COBALT}); CSS: svg{width:90px;image-rendering:pixelated}

// 2) agent sprite (8x8, 4 cols mirrored). A1 cobalt (lead), rest ink (off-white on dark).
const AGENTS={
 a1:[[0,0,1,0],[1,1,1,1],[1,1,1,1],[1,0,1,1],[1,1,1,1],[1,1,1,1],[1,0,0,1],[0,0,0,0]],
 a2:[[0,0,1,0],[0,1,1,1],[1,1,1,1],[0,1,0,1],[0,1,1,1],[1,1,1,0],[0,0,1,0],[0,0,0,0]],
 a3:[[0,0,1,0],[0,0,1,1],[0,1,1,1],[0,1,0,1],[0,1,1,1],[1,1,1,1],[1,0,1,0],[0,0,0,0]],
 a4:[[1,0,0,0],[1,1,0,0],[0,1,1,1],[0,1,1,1],[1,1,0,1],[0,1,1,1],[0,1,0,1],[0,0,0,0]],
 a5:[[0,0,1,0],[0,0,1,1],[0,1,1,1],[1,1,0,1],[1,1,1,1],[1,1,1,1],[1,0,0,1],[0,0,0,0]],
 a6:[[0,0,1,1],[0,1,1,1],[1,1,1,1],[1,1,0,1],[1,1,1,1],[0,1,1,1],[0,0,1,1],[0,0,0,0]]};
function agentSVG(key,color){ const d=AGENTS[key]||AGENTS.a1; let r='';
  for(let y=0;y<8;y++)for(let x=0;x<4;x++){ if(d[y][x]){
    r+=`<rect x="${x}" y="${y}" width="1" height="1" fill="${color}"/>`;
    r+=`<rect x="${7-x}" y="${y}" width="1" height="1" fill="${color}"/>`; } }
  return `<svg viewBox="0 0 8 8" shape-rendering="crispEdges">${r}</svg>`; }

// 3) dot-texture bg (light): background-image:radial-gradient(rgba(11,11,15,.06) 1px,transparent 1px);background-size:11px 11px;
//    dark: rgba(242,243,245,.05). ASCII signature: inline assets/ascii/gs-ascii.js and use GSAscii.field / box / agent.
```

### Designing a pixel icon
12×12 grid, ink body + one cobalt accent pixel-cluster (the "point" of the icon). Keep shapes simple and recognisable (bulb, stacked blocks, broom, rising bars, shield). Symmetry where it helps. Example (lightbulb, cobalt filament):
```
["....kkkk....","..kk....kk..",".k........k.","k....oo....k",
 "k...o..o...k","k...o..o...k",".k..o..o..k.",".k...oo...k.",
 "..k......k..","...kkkkkk...","...k....k...","...kkkkkk..."]
```

## Workflow
1. Build the page (normal scrollable, or square only if asked). Save it wherever you keep build output.
2. **Verify before delivering** - headless screenshot in Chrome (`--headless --screenshot --window-size=...`), Read the PNG, check nothing clips and the icons render crisp. Fix, re-shoot. Delete the scratch PNG.
3. Auto-open in Chrome (`start chrome "C:\full\path.html"`). It's ready to screenshot.
