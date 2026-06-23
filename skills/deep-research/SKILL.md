---
name: deep-research
description: "Multi-source synthesis on a topic: web, GitHub, Twitter/X, YouTube, and Obsidian vault. Outputs a comprehensive research report saved to `wiki/research/`."
metadata:
  hermes:
    category: research
---

# deep-research

**Trigger**: `/deep-research <topic>` or "deep research on", "research across sources"
**Domain**: research
**Automation**: local (on-demand) or remote (scheduled topic tracking)

## Description
Multi-source synthesis on a topic: web, GitHub, Twitter/X, YouTube, and Obsidian vault. Outputs a comprehensive research report saved to `wiki/research/`.

## Instructions
1. Accept topic query from user.
2. Check Obsidian vault first: search `wiki/` for existing notes on topic (avoid duplicate research).
3. Gather from sources in parallel:
   - **Web**: Search 5-10 authoritative sources. Summarize each.
   - **GitHub**: Search repos, issues, READMEs related to topic. Note trending repos, key contributors.
   - **Twitter/X**: Search recent threads (last 7 days). Extract key opinions/links.
   - **YouTube**: Find top 3 relevant videos. Extract titles + descriptions for `yt-research` follow-up.
4. Synthesize into a unified report:
   - Executive summary (5 sentences max)
   - Source breakdown by platform
   - Consensus view + dissenting views
   - Open questions / gaps
   - Recommended next actions
5. Save to `wiki/research/YYYY-MM-DD-deep-<slug>.md`.
6. Append synthesis entry to `domains/research/learnings.md`.
7. Log to `domains/research/eval.json` with fields: topic, sources_count, date, quality_score (self-assess 1-5).

## Input
- Topic string (required)
- Optional: `--sources web,github,twitter` to limit sources
- Optional: `--depth quick|standard|deep` (default: standard)

## Output
```markdown
---
domain: research
date: YYYY-MM-DD
topic: <topic>
sources: [web, github, twitter, youtube]
summary: <one-line synthesis>
tags: [tag1, tag2]
---
# Deep Research: <Topic>
## Executive Summary
## Web Sources
## GitHub Findings
## Twitter/X Threads
## YouTube Queue
## Synthesis
## Open Questions
## Next Actions
```

## Automation
Remote: Schedule weekly deep-research on recurring topics (e.g., "AI agents", "Next.js updates") via GitHub Actions cron → push report to `wiki/research/`.
