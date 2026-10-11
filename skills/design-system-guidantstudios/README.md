# design-system-guidantstudios

Guidant Studios' locked visual language for AI agents. Type `/design-system-guidantstudios <anything>` and the agent builds it in the house style.

- **Palette:** Originals Cobalt `#1433D6` on gallery white `#F6F6F3`, ink `#0B0B0F`, silver as a material only
- **Type:** Archivo (normal + Expanded uppercase), JetBrains Mono, Doto for stats
- **Signature:** an ASCII layer (fields, photo-to-ASCII, ASCII agents, box frames, rules, scramble, animated backgrounds)
- **Material:** silver foil surfaces + a WebGL liquid-silver frame, rationed to one per view
- **Base:** the full robo system (dot-matrix halftone, 6 pixel agents, pixel icons, line-art scenes, 11 dot backgrounds, particle typography, 5 interactive effects), re-skinned

## Install

```bash
cp -r design-system-guidantstudios ~/.claude/skills/
```

Project-scoped: `cp -r design-system-guidantstudios your-project/.claude/skills/`

## Open first

| File | What |
|---|---|
| `SKILL.md` | The locked rules: colours, type, spacing, corners, shadows, buttons, cards, ASCII, metal, agents, starter block, the NOT list, pre-flight |
| `brand-book.html` | The style documenting itself |
| `assets/starter.html` | Page template every build starts from |
| `components/gallery.html` | 36 components with copy-paste snippets |
| `references/ascii-lab.html` | ASCII tools: recipe twins, image → ASCII (txt/png), frames, agents, backgrounds |

Serve the folder locally to view the HTML files (fonts load from Google Fonts):

```bash
python -m http.server 8765 --directory ~/.claude/skills/design-system-guidantstudios
```

## Routing

`SKILL.md` is the baseline. It routes to `lite.md` (quick pages), `slides.md`, `apps.md`, `courses.md`, `infographic.md` and `backgrounds.md`.

## Credits + licences

- Built on **robo** by RoboNuggets - CC BY 4.0 (`LICENSE`)
- `assets/metal/`: metal-fx (MIT, Jakub Antalik), Paper Shaders liquidMetal (Apache-2.0), React (MIT) - notices alongside
- Fonts: Archivo, JetBrains Mono, Doto - SIL Open Font License via Google Fonts
- The Pixel G mark is a placeholder until the official Guidant Studios logo is supplied
