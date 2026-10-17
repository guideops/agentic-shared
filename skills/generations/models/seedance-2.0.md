# Seedance 2.0 (ByteDance)

- Text: `bytedance/seedance-2.0/text-to-video` · Image: `bytedance/seedance-2.0/image-to-video`
  · References: `bytedance/seedance-2.0/reference-to-video` · Fast variants: insert `/fast/`
  (e.g. `bytedance/seedance-2.0/fast/text-to-video`).
- Cost per second: **720p ≈ $0.30**, **1080p ≈ $0.68**; fast 720p ≈ $0.24. Priciest
  option here; confirm resolution and duration first.
- Inputs: `prompt`, `duration` (`auto` or `"4"`…`"15"`), `resolution` (`480p` | `720p`
  default | `1080p` | `4k`), `aspect_ratio` (`auto`, `21:9`, `16:9`, `4:3`, `1:1`, `3:4`,
  `9:16`), `generate_audio`. Image to video: `image_url` (+ optional `end_image_url`).
  Reference to video: `image_urls`, `video_urls`, `audio_urls`. The helper only sends
  local images; video/audio references need public URLs.
