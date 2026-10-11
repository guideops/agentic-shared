# /design-system-guidantstudios lite - quick, discardable HTML

**Trigger:** "/design-system-guidantstudios lite", "gs lite", or any Guidant Studios HTML you call quick / throwaway / scratch / summary.

**Token rule:** for lite jobs read **ONLY this file**. Do NOT read SKILL.md, the other sub-guides or the references. Everything needed for a clean one-pager is below. (Pull SKILL.md only if you want canvas art, ASCII fields or metal.)

**Use for:** summaries, decision docs, one-pagers, comparison tables, quick reports.

## What lite drops vs the full system
- No canvas halftone, no ASCII engine, no metal, no animation. One static ASCII rule is allowed (pure CSS/text, below).
- No marquee. Doto emphasis (1-2 words) + Archivo only.
- Otherwise the same palette, type, corners, slabs and cobalt discipline.

## Drop-in template (copy, fill the `<main>`)
```html
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TITLE</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='8' fill='%231433d6'/%3E%3Cpath d='M17 11h6v6h-6zM23 11h6v6h-6zM29 11h6v6h-6zM35 11h6v6h-6zM41 11h6v6h-6zM11 17h6v6h-6zM11 23h6v6h-6zM11 29h6v6h-6zM29 29h6v6h-6zM35 29h6v6h-6zM41 29h6v6h-6zM47 29h6v6h-6zM11 35h6v6h-6zM47 35h6v6h-6zM11 41h6v6h-6zM47 41h6v6h-6zM17 47h6v6h-6zM23 47h6v6h-6zM29 47h6v6h-6zM35 47h6v6h-6zM41 47h6v6h-6z' fill='%23fff'/%3E%3C/svg%3E">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..800&family=JetBrains+Mono:wght@400;500&family=Doto:wght@900&display=swap" rel="stylesheet">
<style>
:root{--bg:#f6f6f3;--surface:#ffffff;--text:#0b0b0f;--muted:#5d6069;--line:#d7d8dc;--accent:#1433d6;}
html{color-scheme:light;} *{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font:400 16px/1.6 'Archivo',system-ui,sans-serif;}
::selection{background:var(--accent);color:#fff;}
.wrap{max-width:960px;margin:0 auto;padding:64px 32px 96px;}
.kicker{font-stretch:125%;font-weight:600;letter-spacing:.18em;text-transform:uppercase;font-size:11px;color:var(--muted);}
h1{font-weight:700;letter-spacing:-.04em;font-size:clamp(36px,5.5vw,64px);line-height:.98;margin:12px 0 16px;}
h2{font-weight:700;letter-spacing:-.03em;font-size:28px;line-height:1.05;margin:48px 0 16px;}
h3{font-weight:600;font-size:18px;letter-spacing:-.01em;margin-bottom:8px;}
p,li{max-width:68ch;} .muted{color:var(--muted);}
.lead{font-size:19px;color:var(--muted);}
.doto{font-family:'Doto',monospace;font-weight:900;color:var(--accent);margin:0 .18em;}
.mono{font-family:'JetBrains Mono',monospace;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px;margin-top:24px;}
.card{border:2px solid var(--text);border-radius:4px;background:var(--surface);padding:20px 24px;box-shadow:6px 6px 0 var(--text);}
.card.hot{border-color:var(--accent);box-shadow:6px 6px 0 var(--accent);}
.card.hot h3{color:var(--accent);}
.big{font-family:'Doto',monospace;font-weight:900;font-size:40px;line-height:1;letter-spacing:1px;}
.big.hot{color:var(--accent);}
table{width:100%;border-collapse:collapse;margin-top:16px;font-size:15px;}
th,td{text-align:left;padding:12px;border-bottom:1px solid var(--line);}
th{font:500 11px/1 'JetBrains Mono',monospace;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);}
tr.hot td{background:rgba(20,51,214,.08);}
td.num{text-align:right;font:500 14px 'JetBrains Mono',monospace;}
.tag{display:inline-block;border:1.5px solid currentColor;border-radius:2px;padding:4px 8px;font:500 11px/1 'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.04em;}
.tag.hot{color:var(--accent);}
.rule{font:400 12px/1 'JetBrains Mono',monospace;color:var(--muted);white-space:nowrap;overflow:hidden;width:0;min-width:100%;margin:48px 0;}
.rule::before{content:"+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+";}
ol,ul{margin:12px 0 0 22px;} li{margin:6px 0;}
</style></head>
<body><div class="wrap"><main>
  <div class="kicker">KICKER</div>
  <h1>heading with <span class="doto">emphasis</span></h1>
  <!-- content; use <div class="rule"></div> between major blocks -->
</main></div></body></html>
```

## Style rules (same as the full system)
- Palette is LOCKED: bg `#f6f6f3`, surface `#ffffff`, text `#0b0b0f`, muted `#5d6069`, line `#d7d8dc`, cobalt `#1433d6`. No other colours.
- **Cobalt = ONE highlight**: the recommended option, the key number. If nothing needs highlighting, everything stays ink on white.
- Headings Archivo 700, `-0.04em`/`-0.03em`, sentence case or lowercase. Body Archivo 400. Kickers Archivo Expanded 600, uppercase, `.18em`.
- Doto 900 (cobalt) for 1-2 emphasis words or a big number only. JetBrains Mono for tags, table heads, numerics.
- Radius 4px (cards), 2px (tags). Shadows are hard zero-blur slabs.
- Keep it light: short lines, cards and tables over paragraph walls.
- **Favicon ALWAYS**: the Pixel G tile is in the template.
