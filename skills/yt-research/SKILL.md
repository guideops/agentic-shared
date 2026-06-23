---
name: yt-research
description: "Convert a YouTube URL into a structured Obsidian note saved to `wiki/research/`. Extracts transcript, generates summary, key points, quotes, and action items."
metadata:
  hermes:
    category: research
---

# yt-research

**Trigger**: `/yt-research <YouTube URL>` or "summarize this YouTube video", "research this video"
**Domain**: research
**Automation**: local (on-demand)

## Description
Convert a YouTube URL into a structured Obsidian note saved to `wiki/research/`. Extracts transcript, generates summary, key points, quotes, and action items.

## Instructions
1. Accept YouTube URL from user.
2. Fetch transcript via `yt-dlp --write-auto-sub --sub-lang en --skip-download <URL>` or use web fetch on `youtube.com/watch?v=<id>` to get description/metadata.
3. If transcript unavailable, prompt user to paste it manually.
4. Generate structured note:
   - Title: video title
   - Summary: 3-5 sentence TL;DR
   - Key Points: bulleted list (max 10)
   - Quotes: notable direct quotes with timestamps
   - Action Items: anything actionable for user's domains
   - Tags: auto-infer from content (e.g., #ai, #cybersecurity, #nextjs)
5. Save to `wiki/research/YYYY-MM-DD-<slug>.md` with frontmatter.
6. Append entry to `domains/research/learnings.md`.

## Input
- YouTube URL (required)
- Optional: focus area ("focus on cybersecurity parts")

## Output
```markdown
---
domain: research
date: YYYY-MM-DD
source: <YouTube URL>
summary: <one-line>
tags: [tag1, tag2]
---
# <Video Title>
## Summary
## Key Points
## Quotes
## Action Items
```
Saved to: `wiki/research/YYYY-MM-DD-<slug>.md`

## Automation
None by default. Can be chained after `daily-digest` to auto-process queued URLs.
