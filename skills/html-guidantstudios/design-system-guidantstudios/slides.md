# /design-system-guidantstudios - Slides

Slide/deck rules. The **baseline** (palette, type, dot-matrix, cards, pixel icons, canvas gotchas) lives in `DESIGN-SYSTEM.md` and applies here too - this file adds the deck-only composition rules. When you want "/design-system-guidantstudios slides" or a "GS deck", build with the baseline + everything below.

**MINIMAL TEXT IS THE DEFAULT (locked 2026-06-19).** Default every slide to the fewest words possible - ideally a heading + one visual, no body copy. A slide that needs a sentence to land is two slides, or it's the visual doing too little. Add supporting text only when the slide genuinely can't make its point without it. This is the locked default; only deviate when a text-heavy slide is requested. (Reinforces Layout rule 3 below.)

## Layout rules

1. **No kickers / sub-prefixes by default (locked 2026-06-12).** Don't add module codes, section labels, or kicker lines above the heading (e.g. "M1 - Foundations & Setup"). One header text per slide is enough, unless a kicker is explicitly requested.
2. **Centered by default (locked 2026-06-12; hardened 2026-06-15).** Slides compose around the horizontal center: heading, supporting line, and the visual block all centered on the canvas. This is the LOCKED default - do NOT left-align a new deck just because an older reference deck happens to be left-aligned. Concrete recipe:
   ```css
   .slide { display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; }
   .stage { display:grid; grid-template-columns:auto auto; justify-content:center; gap:clamp(28px,3vw,48px); align-items:center; }
   .stage.solo { grid-template-columns:auto; justify-items:center; }
   .labels { text-align:left; }   /* reset: list rows read left, the block stays centered */
   ```
   **Never size a canvas+labels stage as `1fr auto`** - the `1fr` column stretches and strands the label block against the far right edge, miles from the visual (flagged 2026-06-15). Size both columns to content (`auto auto`) and center the pair as a group so the labels hug the visual. **Label text isn't tiny:** description lines ≥16px, titles ~26px - undersized labels were the other half of that same flag. Left-aligned layouts are the rare exception (a true half/half split). Inside cards/list rows the text stays left-aligned for readability - it's the blocks that center, plus the headings.
3. **Less text is the rule.** Title ≤6 words, supporting line ≤10 words and only if essential. Most slides: heading + one visual. If it reads like a sentence, cut it.
4. **No corner texts.** No version tags, no watermarks, no folio labels, no slide numbers. The canvas stays clean.
5. **Static by default.** No reveals, no floats, no sweeps. Professional print energy. The ONE sanctioned exception beyond the agent-icon bob: animated dot matrices per the Motion Extension below - sparing, opt-in, only when motion proves the slide's point.
6. **One idea per slide.**
7. **Mix backgrounds across the deck**: mostly gallery white; ink slides for emphasis beats; **cobalt panels** (everything white) for the big statement beats - max one per three slides; half/half splits (`grid-template-columns: 1fr 1fr`) for variety. A foil slide (`.foil.crumple`, PACE+ silver) is allowed once per deck for a launch / "coming soon" / product beat.
10. **One signature per slide:** an ASCII element OR a metal element, never both. Across a deck, ASCII should appear more often than metal (ASCII leads).
8. Scroll-snap slides, 100vh each, single HTML file, no build step.
9. **Arrow-key nav, trackpad stays live (locked 2026-06-15).** Up/Down arrows move exactly one slide. **Do NOT block the wheel/trackpad** - an earlier wheel-block was reversed; normal scroll should keep working, and `scroll-snap` makes it land one slide at a time anyway. Wire the snippet below into every deck for the arrow keys; leave scrolling alone.

**Arrow-key nav snippet (LOCKED 2026-06-15)** - paste into the deck's script after the slide-id list (`ids`) is defined. If the deck has no `ids` array, build one first: `const ids = [...document.querySelectorAll('.slide')].map(s => s.id);`

```js
/* arrow keys move one slide; wheel/trackpad scroll is left alone */
(function () {
  const secs = ids.map(id => document.getElementById(id)).filter(Boolean);
  if (!secs.length) return;
  const near = () => secs.reduce((b, s, i) =>
    Math.abs(s.getBoundingClientRect().top) < Math.abs(secs[b].getBoundingClientRect().top) ? i : b, 0);
  const go = d => secs[Math.max(0, Math.min(secs.length - 1, near() + d))].scrollIntoView({ behavior: 'smooth' });
  addEventListener('keydown', e => {
    if (e.key === 'ArrowDown' || e.key === 'PageDown') { e.preventDefault(); go(1); }
    else if (e.key === 'ArrowUp' || e.key === 'PageUp') { e.preventDefault(); go(-1); }
  });
})();
```

Keep `scroll-snap-type:y mandatory` on `html` so both the arrow jumps AND normal trackpad/wheel scroll lock cleanly onto each slide. The dot nav and anchor links work too.

## Motion Extension (added 2026-06-11)

Animated dot matrices - pixel-tile panels rebuilt in /design-system-guidantstudios language. **Use sparingly - only when motion proves the slide's point** (something flowing, breathing, coming together). Default stays static; a deck should have at most 1-2 animated slides, often zero. PDFs and print exports are always static.

**The four motion principles (LOCKED):**

1. **The grid never moves.** Dots stay pinned to their grid positions. Only radius and color change over time. Nothing slides, translates, or sweeps - that discipline is what separates this from generic motion graphics.
2. **Time goes into the brightness function.** Motion is just `fn(u, v, t)` instead of `fn(u, v)`. Every static recipe (sphere, wave, hexagon, arrow, bars...) can be animated by threading `t` through it.
3. **Slow cycles, print energy kept.** 6-8 second loops, sine-eased. Any paused frame must look like a finished static /design-system-guidantstudios slide. No frame is ever mid-transition junk.
4. **One motion per slide.** Mirrors the one-idea-per-slide rule.

**Animated engine variant** - same halftone engine, returns a draw function instead of drawing once; drive all slides from a single `requestAnimationFrame` loop:

```js
function makeHalftone(id, w, h, step, maxR, color, fn, color2, fn2){
  const c=document.getElementById(id); if(!c) return null;
  const ctx=c.getContext('2d'); const dpr=window.devicePixelRatio||1;
  c.width=w*dpr; c.height=h*dpr; c.style.width=w+'px'; c.style.height=h+'px'; ctx.scale(dpr,dpr);
  return function(t){            // t in seconds
    ctx.clearRect(0,0,w,h);
    for(let y=step/2;y<h;y+=step) for(let x=step/2;x<w;x+=step){
      const u=x/w, v=y/h;
      let b=fn(u,v,t), col=color;
      if(fn2){const b2=fn2(u,v,t); if(b2>b){b=b2; col=color2;}}
      if(b<=0.02) continue;
      ctx.fillStyle=col; ctx.beginPath(); ctx.arc(x,y,Math.min(maxR,b*maxR),0,Math.PI*2); ctx.fill();
    }
  };
}
// const draws=[d1,d2,d3]; requestAnimationFrame loop calls each with elapsed seconds.
```

**Motion verb library:**
- **BREATHE** - sphere whose lambert light vector slowly orbits (6s); optional small cobalt hot-spot riding the light. For "alive / steady state".
- **FLOW** - wave with phase drifting through (8s) + one cobalt pulse traveling the crest per cycle. For direction, throughput, pipelines.
- **RESOLVE** - shape (e.g. a hexagon mark) condenses out of `pn()` noise via a smoothstepped order parameter k (noise→shape→hold→dissolve, 8s); cobalt edge fades in with the shape. For "it comes together" moments.
- Extendable with the same one-line `t` pattern: RADIATE (sunburst rays sweep), GROW (bars fill), CHARGE (density builds). Name new verbs when inventing them.

**Full-screen animated backgrounds** (behind a hero/section): see **`backgrounds.md`** - 11 named, reusable dot-matrix backgrounds (SWELL, RAIN, SCANLINE, TIDE, GATEWAY, MOIRÉ, COMET, HONEYCOMB, TILES, SPRITE MARCH, MORPH MARK) with the only-the-visible-one-animates engine. Live gallery: `references/dot-backgrounds.html`.

All static rules still apply during motion: text-over-dots opacity rule, two layers max, `pn()` not `Math.random()`, palette, banned ring shape.

## Slide workflow

1. Parse brief → slide list (one idea each, aggressive text cuts).
2. Single HTML file; output to the relevant project folder (or an output folder for ad-hoc). Scroll-snap + dot nav on the right (dots only, no labels).
3. Pick per slide: bg (white / ink / cobalt / split / foil), display voice (Doto emphasis OR Archivo Expanded marquee OR neither), one visual (dot-matrix, line-art, ASCII field, or agents).
4. Compose new brightness functions for concepts not in the recipe library.
5. Open in Chrome (`start chrome "<path>"`) when done.
6. `/tweak [N]` style revisions: edit only that slide's section + its canvas function.
