/* gs-ascii.js - Guidant Studios ASCII layer (the signature feature). No dependencies.
   Inline it in single-file builds, or <script src="assets/ascii/gs-ascii.js"></script>.
   Everything renders in JetBrains Mono. Colours are read from CSS vars (--text, --accent) at draw time.

   API (window.GSAscii):
     field(el, {cols, rows, fn, fn2, ramp})      brightness fn(u,v)->0..1 as characters (the ASCII twin of halftone())
     fromImage(el, img, {cols, ramp, invert, contrast})  photo/artwork -> ASCII
     agent(key, {on, off})                       agent sprite A1-A6 as a block-character string
     box(lines, {style, pad, title})             box-drawn frame string (single | double | heavy | ascii)
     rule(el, pattern)                           fill an element with a repeating divider pattern
     scramble(el, {duration})                    decode a word from random glyphs into its real text
     bg(canvas, {mode, cell, strength})          animated character background: 'swell' | 'drift' | 'rain' (strength = max field alpha, default .3)
     init(scope)                                 wire data-attributes (runs automatically on load)

   Data attributes (zero JS needed):
     <pre data-ascii-agent="a1"></pre>
     <div class="ascii-rule" data-ascii-rule="+-"></div>
     <span data-ascii-scramble>studios</span>            (on scroll-in; ="hover" to replay on hover)
     <canvas data-ascii-bg="swell"></canvas>
*/
(function () {
  const RAMP = ' .:-=+*#%@';          // light -> dense
  const RAMP_BLOCK = ' ░▒▓█';
  const GLYPHS = '!<>-_\\/[]{}=+*^?#01ABCDEFGHJKLMNPRSTUVXYZ';
  const reduced = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const css = (name, el) => getComputedStyle(el || document.documentElement).getPropertyValue(name).trim();
  const esc = c => c === '&' ? '&amp;' : c === '<' ? '&lt;' : c === '>' ? '&gt;' : c;
  const pick = (ramp, b) => ramp[Math.max(0, Math.min(ramp.length - 1, Math.round(b * (ramp.length - 1))))];
  function pn(x, y) { const v = Math.sin(x * 127.1 + y * 311.7) * 43758.5453; return v - Math.floor(v); }

  const AGENTS = {
    a1: [[0,0,1,0],[1,1,1,1],[1,1,1,1],[1,0,1,1],[1,1,1,1],[1,1,1,1],[1,0,0,1],[0,0,0,0]],
    a2: [[0,0,1,0],[0,1,1,1],[1,1,1,1],[0,1,0,1],[0,1,1,1],[1,1,1,0],[0,0,1,0],[0,0,0,0]],
    a3: [[0,0,1,0],[0,0,1,1],[0,1,1,1],[0,1,0,1],[0,1,1,1],[1,1,1,1],[1,0,1,0],[0,0,0,0]],
    a4: [[1,0,0,0],[1,1,0,0],[0,1,1,1],[0,1,1,1],[1,1,0,1],[0,1,1,1],[0,1,0,1],[0,0,0,0]],
    a5: [[0,0,1,0],[0,0,1,1],[0,1,1,1],[1,1,0,1],[1,1,1,1],[1,1,1,1],[1,0,0,1],[0,0,0,0]],
    a6: [[0,0,1,1],[0,1,1,1],[1,1,1,1],[1,1,0,1],[1,1,1,1],[0,1,1,1],[0,0,1,1],[0,0,0,0]]
  };

  /* 1. Brightness field -> characters. Same recipe functions as the halftone engine.
     Keep shapes round: rows = round(cols * 0.6 * boxHeight / boxWidth) at line-height 1. */
  function field(el, { cols = 72, rows = 28, fn, fn2, ramp = RAMP } = {}) {
    let out = '';
    for (let y = 0; y < rows; y++) {
      let line = '', open = false;
      for (let x = 0; x < cols; x++) {
        const u = (x + .5) / cols, v = (y + .5) / rows;
        let b = fn(u, v), hot = false;
        if (fn2) { const b2 = fn2(u, v); if (b2 > b) { b = b2; hot = true; } }
        const ch = b <= .02 ? ' ' : esc(pick(ramp, b));
        if (hot && !open) { line += '<b class="ascii-hot">'; open = true; }
        if (!hot && open) { line += '</b>'; open = false; }
        line += ch;
      }
      out += line + (open ? '</b>' : '') + '\n';
    }
    el.innerHTML = out;
    return out;
  }

  /* 2. Image -> ASCII. Dense characters = dark pixels on light pages; pass invert:true on dark pages. */
  function fromImage(el, img, { cols = 100, ramp = RAMP, invert = false, contrast = 1.15 } = {}) {
    const rows = Math.round(cols * (img.naturalHeight || img.height) / (img.naturalWidth || img.width) * 0.6);
    const c = document.createElement('canvas'); c.width = cols; c.height = rows;
    const ctx = c.getContext('2d', { willReadFrequently: true });
    ctx.drawImage(img, 0, 0, cols, rows);
    const d = ctx.getImageData(0, 0, cols, rows).data;
    let out = '';
    for (let y = 0; y < rows; y++) {
      for (let x = 0; x < cols; x++) {
        const i = (y * cols + x) * 4;
        let l = (0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]) / 255;
        l = Math.max(0, Math.min(1, (l - .5) * contrast + .5));
        out += esc(pick(ramp, invert ? l : 1 - l));
      }
      out += '\n';
    }
    el.innerHTML = out;
    return out;
  }

  /* 3. Agents as solid block characters (still SOLID - never a ramp/halftone agent). 2 chars per pixel = square cells. */
  function agent(key, { on = '██', off = '  ' } = {}) {
    const d = AGENTS[key] || AGENTS.a1;
    return d.slice(0, 7).map(r => [0,1,2,3,3,2,1,0].map((c, i) => r[i < 4 ? i : 7 - i] ? on : off).join('')).join('\n');
  }

  /* 4. Box-drawn frames. */
  const BOX = {
    single: '┌┐└┘─│', double: '╔╗╚╝═║', heavy: '┏┓┗┛━┃', ascii: '++++-|'
  };
  function box(lines, { style = 'single', pad = 1, title = '' } = {}) {
    lines = [].concat(lines);
    const [tl, tr, bl, br, h, v] = BOX[style] || BOX.single;
    const w = Math.max(title.length + 4, ...lines.map(l => l.length)) + pad * 2;
    const top = title ? tl + h + ' ' + title + ' ' + h.repeat(w - title.length - 3) + tr : tl + h.repeat(w) + tr;
    const body = lines.map(l => v + ' '.repeat(pad) + l.padEnd(w - pad * 2) + ' '.repeat(pad) + v);
    return [top, ...body, bl + h.repeat(w) + br].join('\n');
  }

  /* 5. Divider rules - element clips the overflow (CSS .ascii-rule). */
  function rule(el, pattern = '+-') { el.textContent = pattern.repeat(Math.ceil(600 / pattern.length)); }

  /* 6. Scramble-decode. One per heading block; never on body copy. */
  function scramble(el, { duration = 900 } = {}) {
    const final = el.dataset.asciiFinal || (el.dataset.asciiFinal = el.textContent);
    if (reduced()) { el.textContent = final; return; }
    const t0 = performance.now();
    (function tick(t) {
      const p = Math.min(1, (t - t0) / duration);
      el.textContent = [...final].map((ch, i) => ch === ' ' || i / final.length < p ? ch : GLYPHS[(Math.random() * GLYPHS.length) | 0]).join('');
      if (p < 1) requestAnimationFrame(tick);
    })(t0);
  }

  /* 7. Animated character background (counts as THE one animated effect on the page). */
  function bg(canvas, { mode = 'swell', cell = 14, accentFrac = .05, strength = .3 } = {}) {
    const ctx = canvas.getContext('2d');
    let W = 0, H = 0, cols = 0, rows = 0, drops = [], visible = true, raf = 0;
    const size = () => {
      const r = canvas.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
      W = r.width; H = r.height; canvas.width = W * dpr; canvas.height = H * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cols = Math.ceil(W / (cell * .62)); rows = Math.ceil(H / cell);
      drops = Array.from({ length: cols }, (_, i) => pn(i, 7) * rows);
    };
    const draw = t => {
      const ink = css('--text', canvas) || '#0b0b0f', acc = css('--accent', canvas) || '#1433d6';
      ctx.clearRect(0, 0, W, H);
      ctx.font = `500 ${cell * .86}px 'JetBrains Mono', monospace`; ctx.textBaseline = 'top';
      const cw = cell * .62, s = t / 1000;
      for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++) {
        let b;
        if (mode === 'rain') {
          const head = (drops[x] + s * (4 + pn(x, 3) * 6)) % (rows + 18);
          const d = head - y; b = d >= 0 && d < 14 ? 1 - d / 14 : 0;
        } else if (mode === 'drift') {
          b = .5 + .5 * Math.sin(x * .09 + s * .6 + Math.sin(y * .11 + s * .4) * 2.2) * Math.cos(y * .07 - s * .3);
          b = b * b;
        } else {
          const crest = .66 + .14 * Math.sin(x * .06 + s * .9) + .06 * Math.sin(x * .17 - s * 1.3);
          b = Math.max(0, (y / rows - crest) * 2.4);
        }
        if (b < .08) continue;
        const hot = pn(x, y) < accentFrac && b > .5;
        ctx.globalAlpha = hot ? Math.min(1, strength * 2.6) : Math.min(strength, b * strength * 1.1);
        ctx.fillStyle = hot ? acc : ink;
        ctx.fillText(mode === 'rain' ? GLYPHS[(pn(x, y + Math.floor(s * 6)) * GLYPHS.length) | 0] : pick(RAMP, Math.min(1, b)), x * cw, y * cell);
      }
      ctx.globalAlpha = 1;
    };
    const loop = t => { if (visible) draw(t); raf = requestAnimationFrame(loop); };
    size(); new ResizeObserver(size).observe(canvas);
    new IntersectionObserver(es => { visible = es[0].isIntersecting; }).observe(canvas);
    if (reduced()) draw(2400); else raf = requestAnimationFrame(loop);
    return { redraw: () => draw(performance.now()), destroy: () => cancelAnimationFrame(raf) };
  }

  function init(scope = document) {
    scope.querySelectorAll('[data-ascii-agent]').forEach(el => { el.textContent = agent(el.dataset.asciiAgent); });
    scope.querySelectorAll('[data-ascii-rule]').forEach(el => rule(el, el.dataset.asciiRule || '+-'));
    scope.querySelectorAll('[data-ascii-bg]').forEach(el => { if (!el._gs) el._gs = bg(el, { mode: el.dataset.asciiBg || 'swell', strength: parseFloat(el.dataset.asciiStrength) || .3 }); });
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { scramble(e.target); io.unobserve(e.target); } }), { threshold: .4 });
    scope.querySelectorAll('[data-ascii-scramble]').forEach(el => {
      io.observe(el);
      if (el.dataset.asciiScramble === 'hover') el.addEventListener('mouseenter', () => scramble(el));
    });
  }

  window.GSAscii = { field, fromImage, agent, box, rule, scramble, bg, init, AGENTS, RAMP, RAMP_BLOCK, pn };
  const go = () => (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => init());
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
})();
