# GPT Image 2 (via fal, pay-per-use)

- Generate: `openai/gpt-image-2` · Edit: `openai/gpt-image-2/edit`
- Cost: token-priced (text $5 / $10 per 1M in/out; image $8 / $30 per 1M in/out).
  `quality: high` (the default) costs the most; quote `medium` when the operator wants
  cheaper drafts. Give a rough per-image estimate before running.
- Inputs: `prompt`, `quality` (`auto` | `low` | `medium` | `high`), `image_size`
  (`square_hd`, `portrait_4_3`, `landscape_4_3`, `landscape_16_9`, …), `background`
  (`auto` | `transparent` | `opaque`), `num_images`, `output_format`. Edit requires
  `image_urls` and takes an optional `mask_url`.
- Same model family as Codex's built-in image tool. If the operator is in Codex and
  wants no API charge, use Route B in SKILL.md instead.
