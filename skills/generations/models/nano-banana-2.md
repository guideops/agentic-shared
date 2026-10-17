# Nano Banana 2 (default image model)

- Generate: `fal-ai/nano-banana-2` · Edit / references: `fal-ai/nano-banana-2/edit`
- Cost: **$0.08 per image** (num_images multiplies it).
- Inputs: `prompt` (required), `aspect_ratio` (`auto`, `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, …),
  `resolution` (`0.5K` | `1K` default | `2K` | `4K`), `num_images` (default 1),
  `output_format` (`png` default | `jpeg` | `webp`), `enable_web_search` (current facts,
  e.g. event infographics), `seed`. Edit adds `image_urls` (array).
- Good at: fast iterations, infographics with real text, edits that keep a subject.

```bash
node scripts/fal.mjs --endpoint fal-ai/nano-banana-2 --model nano-banana-2 --name io26_infographic_v1_1 \
  --input '{"prompt":"…","aspect_ratio":"16:9","resolution":"2K"}'
node scripts/fal.mjs --endpoint fal-ai/nano-banana-2/edit --model nano-banana-2 --name io26_infographic_v2_1 \
  --ref generations/refs/antigravity_logo.png --ref-field image_urls \
  --input '{"prompt":"Replace the icon in panel 02 with the logo in the reference","resolution":"2K"}'
```
