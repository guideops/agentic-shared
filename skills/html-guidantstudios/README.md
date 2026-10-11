# html-guidantstudios

A Claude skill that teaches your agent to produce **HTML output instead of markdown** across four levels of capability, with every file built in the **Guidant Studios** visual language.

It's a copy of the `html` skill with its design system swapped from design-system-x to **design-system-guidantstudios**. The framework, levels, recipes and export contract are unchanged.

Based on [Thariq Shihipar](https://x.com/trq212)'s article [_Using Claude Code: The Unreasonable Effectiveness of HTML_](https://x.com/trq212/status/2052809885763747935). Examples gallery: **[thariqs.github.io/html-effectiveness](https://thariqs.github.io/html-effectiveness/)**

---

## The four levels

| Level | What | Examples |
|-------|------|----------|
| **1 - Static Doc** | HTML as a prettier markdown | Specs, reports, explainers, plans |
| **2 - Visual Artifact** | Adds SVG, tables, layouts | Design systems, decks, dashboards |
| **3 - Two-Way Interactive** | Sliders/toggles + export button | Tuning, A/B picks, prompt iteration |
| **4 - Throwaway Tool** | Purpose-built mini-app | Triage boards, config editors |

## Visual language: design-system-guidantstudios

- **Colour:** Originals Cobalt `#1433D6` on gallery white `#F6F6F3`, ink `#0B0B0F`. Light by default, with a dark toggle
- **Type:** Archivo (normal width for reading, Expanded uppercase for kickers and buttons), JetBrains Mono for code, data and ASCII, Doto for stats
- **Signature:** an ASCII layer in every file: scrambled kickers, `+-+-` dividers, ASCII hero fields, ASCII agents, box-framed logs
- **Material:** silver foil or a liquid-metal frame, at most one per view and never alongside ASCII
- **Shape:** 4px corners, hard zero-blur slab shadows, one cobalt highlight per view

What's in the folder:
- `design-system-guidantstudios/` - bundled copy of the standalone skill (`SKILL.md` renamed to `DESIGN-SYSTEM.md` so it doesn't load as a second skill)
- `assets/starter.html` - the foundation every build starts from, plus the level classes: TL;DR, TOC, callouts, tables, code, figures, pick cards, comment boxes, tri-state status, tool shell, export bar, slides, print

When you change the standalone `design-system-guidantstudios` skill, copy it in here too.

## Install

```bash
cp -r html-guidantstudios ~/.claude/skills/
```

## Triggers

- `/html-guidantstudios`
- "html guidant studios" / "gs html"
- "build me an html for X in studio style"

Plain `/html` still goes to the original `html` skill.

## Credit

- Framework and use-case taxonomy: **[Thariq Shihipar](https://x.com/trq212)**
- Original `html` skill and robo design system: [RoboNuggets](https://robonuggets.com) (MIT for this skill, `LICENSE`; robo is CC BY 4.0, see `design-system-guidantstudios/LICENSE`)
- Guidant Studios re-skin: Guidant Operations
