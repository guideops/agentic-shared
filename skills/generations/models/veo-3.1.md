# Veo 3.1 (Google, via fal)

> fal deprecates these endpoints on **2026-11-17**. Prefer Kling 3.0 or Seedance 2.0
> for anything that must keep working after that date.

- Text: `fal-ai/veo3.1` · Image: `fal-ai/veo3.1/image-to-video` · Fast: `fal-ai/veo3.1/fast`,
  `fal-ai/veo3.1/fast/image-to-video`
- Cost per second (720p/1080p): **$0.20 silent / $0.40 with audio**; fast $0.10 / $0.15.
  An 8s clip with audio ≈ $3.20.
- Inputs: `prompt`, `duration` (`4s` | `6s` | `8s` default), `resolution` (`720p` default |
  `1080p` | `4k`), `aspect_ratio` (`16:9` | `9:16`), `generate_audio` (default true),
  `negative_prompt`, `seed`. Image to video requires `image_url`.
