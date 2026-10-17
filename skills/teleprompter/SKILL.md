---
name: teleprompter
description: "Send scripts to the operator's teleprompter in Agentic Workspace (/teleprompter) so they can read them on their phone and computer while recording. Writes each script as Markdown into the vault's Agentic Output/teleprompter folder, can put several scripts on one long page for a one-take batch recording, switches the open screens to it, and gives the phone and desktop links. Use when the operator says 'send this to my teleprompter', 'put these on the teleprompter', 'teleprompter link', '/teleprompter', or wants to read a script on camera."
metadata:
  hermes:
    category: creative
---

# teleprompter

The operator reads scripts in **Agentic Workspace → Teleprompter** (`/teleprompter`
on desktop, `/teleprompter/phone` full screen on the phone). Both screens stay on
the same line through the workspace server, so they work anywhere on the tailnet —
no shared wifi needed. Adapted from RUBRIC Teleprompter (RoboNuggets, CC BY 4.0).

## Where things live

- **Scripts:** `.md` files in the Obsidian vault at `Agentic Output/teleprompter/`
  (Syncthing carries them between the laptop and the VPS). Print the absolute
  folder with `node "$AW/scripts/teleprompter.js" dir`.
- **The CLI:** `scripts/teleprompter.js` in the Agentic Workspace checkout — `$AW_REPO`,
  else `/root/agentic-workspace`, else the current repo if it contains that script.
  It writes through the workspace's vault ACL lane and switches the open screens.
  Use it rather than writing into the vault by hand.

## Steps

1. **Name the file.** A 2–3 word topic in lowercase kebab-case, ending `.md`, so it
   is easy to find on a phone: `coffee-shop-hook.md`, `pricing-reels-batch.md`.
   Never `script.md` / `video.md` / `untitled.md`. Project or ticket code first if the
   operator uses them (`EP12-goal-hook.md`). Only letters, numbers, spaces, dots,
   dashes and underscores.
2. **Check the name.** `node "$AW/scripts/teleprompter.js" list`. If the name is taken
   by a different topic, pick another. If it is the same topic, ask the operator once:
   replace it (`--replace`) or save a new version (`-v2`).
3. **Write the script** exactly in the operator's words — do not fix grammar, wording
   or punctuation unless asked; they read their own words on camera. Format for
   reading aloud:
   ```md
   # Title of the video

   ## Section name (optional)

   One beat per paragraph. Short paragraphs, a blank line between them.

   Next beat here.
   ```
   `#` shows orange, `##` yellow, `**bold**` orange, a line of `---` draws a divider.
   No padding blank lines at the top or bottom.
4. **Batch recording.** Several scripts for one continuous take (e.g. a week of reels)
   go in ONE file in recording order, each under `## Reel N - <title>` with `---`
   between them, under a `# Reels batch: <topic>` title. Name it for the batch.
5. **Send it** (saves and switches every open phone/desktop page within ~2 s):
   ```bash
   node "$AW/scripts/teleprompter.js" send pricing-reels-batch.md <<'EOF'
   # Reels batch: pricing
   ...
   EOF
   ```
   `--replace` overwrites an existing script (the old copy is kept as `.bak-<time>`);
   `--no-live` saves without switching the screens. To put an existing script back on
   screen: `node "$AW/scripts/teleprompter.js" show <name>.md`.
6. **Give the links** in a few lines:
   - **Desktop:** `<workspace URL>/teleprompter` (or `/teleprompter/desktop` full screen)
   - **Phone:** `<workspace URL>/teleprompter/phone` — any device on the tailnet;
     add it to the home screen for a full-screen prompter.
   - The file name and the vault folder it went to.
   Use the workspace URL the operator normally opens. The page's **Copy phone link**
   button shows the exact address.

## Controls (if asked)

- **Phone:** Play / Pause, speed slider, Size, Mirror (for a mirror rig), Sync, search.
  Hold the orange reading line half a second, then drag it level with the camera lens.
- **Desktop:** Play, Speed, Size; Space plays/pauses, arrows scroll, + / - change speed;
  drag the orange line to eye level.
- Whichever screen was touched last leads; the other follows.

## If something is off

- `No Obsidian vault is configured` — the workspace has no vault path (Setup).
- Phone page asks for a password — it is the workspace's own login, same as every page.
- Screens did not switch — they poll every 2 s; reload the page, or run `show` again.
