# /design-system-guidantstudios - Apps

Guidant Studios style applied to apps, tools, dashboards, and any interactive web UI. The **baseline** (palette, type, dot-matrix, ASCII, metal, cards, pixel icons, gotchas) in `SKILL.md` applies here too - this file adds the app-only rules.

## Dark / light mode toggle - DEFAULT

**Every app ships with a dark/light toggle.** Don't wait to be asked.

- **First-load default = light** (gallery white). The toggle flips to ink dark mode.
- **Accent per mode:** `#1433d6` cobalt in light, `#6f86ff` lifted cobalt in dark (plain cobalt is 2.3:1 on ink - fails). On-accent text: `#ffffff` light / `#0b0b0f` dark.
- **Tokens:** use the full token set from the SKILL.md starter block (`--bg --surface --surface-2 --line --text --muted --accent --on-accent --slab`). No new colours.
- **Persist** the choice in `localStorage` under `gs-theme` (wrap in try/catch).
- **Color-scheme guard:** sync `html { color-scheme }` to the active theme.
- **Redraw canvases + ASCII on flip:** keep `window.gsRedraw` and call it from the toggle. Read `--text` / `--accent` with `getComputedStyle` inside the redraw.

**Drop-in:** the toggle button + script are in `assets/starter.html` (`#themeToggle`, 40px, 2px `--text` border, radius 4px, JetBrains Mono `◐`). Copy them verbatim.

## App-shell defaults

- **Sharp edges.** Buttons, cards, inputs, panels: radius 4px; tags 2px. Baseline card recipe - 2px `--text` border (1px `--line` in dark), hard zero-blur slab. Match the brand book.
- **Archivo for all UI text**; Archivo Expanded uppercase for buttons, kickers, tab labels; **JetBrains Mono for data**: table numerics, IDs, timestamps, logs, status tags. Doto only for a hero stat or 1-2 emphasis words.
- **Cobalt is the single action accent** - primary button, active state, the one thing you want clicked. Same cobalt-discipline rule as slides: if nothing needs highlighting, nothing gets cobalt.
- **Pixel-sprite icons, not vector icon fonts** (baseline `sprite()` engine). Recolor to `var(--text)`, cobalt only for the primary action.
- **ASCII is the app signature.** Empty states = an ASCII agent + one line. Loading = a scramble on a mono label or an ASCII bar `[██████····]`. Logs/agent consoles = ASCII frame cards and `[ run ]` ASCII buttons. Dot-matrix art for hero/data visuals. One feature visual per view.
- **Metal in apps:** at most one round icon button with `data-metal="circle"` (e.g. the main "run" or "send" action) per screen. Never on toolbars, inputs or tables.
- Single HTML file with no build step when the tool is small enough; otherwise follow your project's stack conventions.

## App workflow

1. Parse the brief → screens/views and the one primary action per view.
2. Scaffold the shell from `assets/starter.html`: tokens, fonts, toggle, `gs-ascii.js`. Output to an output folder for ad-hoc tools, or the project folder for real ones.
3. Build views; lead with the data/action, decorate sparingly with dot-matrix art.
4. Wire `window.gsRedraw` if any canvas art is present.
5. Open in Chrome (`start chrome "<path>"`) when done - verify BOTH modes via the toggle before calling it finished.
