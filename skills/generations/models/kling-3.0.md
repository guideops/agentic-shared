# Kling 3.0 (default video model)

- Text to video: `fal-ai/kling-video/v3/{standard|pro}/text-to-video`
- Image to video: `fal-ai/kling-video/v3/{standard|pro}/image-to-video`
- Cost per second: **standard $0.084**, **pro $0.112** (4K variant $0.42). A 5s pro clip
  ≈ $0.56. Quote duration × rate before running.
- Inputs: `prompt`, `duration` (`"3"`…`"15"` as strings, default `"5"`), `aspect_ratio`
  (`16:9` | `9:16` | `1:1`, text-to-video only), `generate_audio` (default true; set false
  for silent b-roll), `negative_prompt`, `cfg_scale`, `multi_prompt` + `shot_type` for
  multi-shot. Image to video requires `start_image_url`, optional `end_image_url`
  (first/last frame control) and `elements` (reference assets).

```bash
node scripts/fal.mjs --endpoint fal-ai/kling-video/v3/pro/image-to-video --model kling-3.0 \
  --name kling3_desk_pan_1 --ref generations/nblm_broll_v1_1.jpg --ref-field start_image_url \
  --input '{"prompt":"Slow dolly across the desk, soft morning light","duration":"5","generate_audio":false}'
```
