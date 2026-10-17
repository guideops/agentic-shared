---
name: generations
description: "Generate images and videos for the Agentic Workspace Generations gallery (/generations) via fal.ai (Nano Banana 2/Pro, GPT Image 2, Kling 3.0, Seedance 2.0, Veo 3.1) or, in Codex, the built-in image_gen tool on the ChatGPT plan. Use when the operator asks to generate/make/create an image, picture, thumbnail, b-roll, video or clip, pastes a Generations 'Prepare in chat' brief, names one of those models, or asks to add a visual style or model to Generations."
metadata:
  hermes:
    category: creative
---

# generations

Media made here lands in **Agentic Workspace → Generations** (`/generations`), which
polls the folder every 5 seconds. Adapted from RUBRIC Generations (Jay E / RoboLabs,
CC BY 4.0); the kit's Kie / Google recipes are replaced by fal.ai and Codex.

## Where things live

- **Output folder:** `<docs root>/generations/`, where the docs root is
  `HERMES_DOCS_DIR`, else `~/Documents/Hermes` (`/root/Documents/Hermes` on the VPS).
  A Generations brief states the absolute folder; use it.
- **References:** `<docs root>/generations/refs/` (the operator drops them on the page).
- **Styles:** built-ins ship with AW (`server/generations/styles.json`). Operator- or
  agent-added styles go in `<docs root>/generations/styles/styles.json` (an array of
  `{id, name, description, prompt, image}`; `image` is a file next to it). Same `id`
  overrides a built-in. Never edit the AW repo to add a style.
- **Models:** `server/generations/models.json` in the AW checkout (`$AW_REPO`, else
  `/root/agentic-workspace`). Per-model notes: `models/*.md` in this skill.

## Hard rules

1. **Cost first.** Before any fal call, tell the operator the model, settings and
   estimated cost (see the model file) and wait for a clear go-ahead. A brief that
   says "confirm the cost" means exactly this. Never loop retries that spend money.
2. Save every result into the output folder with a descriptive kebab/snake name:
   `{project}_{variant}_{attempt}_{timestamp}.{ext}`, videos prefixed with the model
   (`kling3_…`, `seedance2_…`, `veo31_…`). Never overwrite; bump the attempt.
3. Write a sidecar `<same name>.json` with `prompt`, `model`, `endpoint`, `input`
   (no keys, no data URIs) and `created`. The helper does this for you.
4. Never print or echo `FAL_KEY`.

## Route A — fal.ai (default; images and video)

The helper `scripts/fal.mjs` (Node 18+, no dependencies) submits to fal's queue,
polls, downloads the result into the folder and writes the sidecar:

```bash
node "<this skill>/scripts/fal.mjs" \
  --endpoint fal-ai/nano-banana-2 \
  --name launch_hero_v1_1 \
  --input '{"prompt":"…","aspect_ratio":"16:9","resolution":"2K"}' \
  [--ref <file> --ref-field image_urls] [--out-dir <folder>] [--model nano-banana-2]
```

- **Key:** `FAL_KEY` from the environment, else `~/.config/generations/.env`
  (`FAL_KEY=…`). AW chat sessions strip `*_KEY` variables from their children, so in
  AW chat the config file is the source. On the VPS the Vaultwarden secrets sync
  writes it. If neither exists, stop and tell the operator; never ask them to paste
  the key into chat.
- **References:** `--ref` takes local images (repeatable). The helper sends them as
  base64 data URIs downscaled to ≤1600px. fal accepts data URIs on these models'
  image fields, but large payloads are slow. Use `--ref-field` to name the field:
  `image_urls` (Nano Banana edit, GPT Image edit, Seedance reference),
  `start_image_url` (Kling image-to-video), `image_url` (Veo / Seedance
  image-to-video). Use the model's edit or image-to-video endpoint when you pass refs.
- **Styles:** append the style's `prompt` text to your prompt.
- Video jobs take 1–6 minutes; the helper polls for up to 20.

## Route B — Codex on the ChatGPT plan (images only, no API key)

When the brief names **GPT Image (Codex)**, or the operator asks to use their ChatGPT
subscription, and you are Codex: use the built-in `image_gen` tool (see Codex's
`imagegen` system skill), not the CLI fallback, not fal. It saves under
`$CODEX_HOME/generated_images/…`; copy the chosen file into the output folder with a
descriptive name and write the sidecar JSON yourself (`model: "codex-image"`). There
is no per-image charge, but it counts against the plan's limits. Claude Code and
Hermes cannot use this route; hand off to Codex instead.

## Adding a model

Look up the endpoint and its input schema on fal
(`https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=<id>`), add an entry to
`server/generations/models.json` in the AW repo (same fields as the others:
`id, name, type, provider, docs, endpoints, aspect, resolution, mode, duration,
price, features`), and add `models/<id>.md` here. That is a repo change: commit it
on the laptop and deploy as usual.

## Model files

| Model | File | Type |
|---|---|---|
| Nano Banana 2 (default image) | `models/nano-banana-2.md` | image |
| Nano Banana Pro | `models/nano-banana-pro.md` | image |
| GPT Image 2 | `models/gpt-image-2.md` | image |
| Kling 3.0 (default video) | `models/kling-3.0.md` | video |
| Seedance 2.0 | `models/seedance-2.0.md` | video |
| Veo 3.1 (fal retires it 2026-11-17) | `models/veo-3.1.md` | video |
