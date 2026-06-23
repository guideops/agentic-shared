---
name: daily-digest
description: "Automated morning briefing. No user input required. Pulls top content from GitHub trending, Hacker News, Twitter/X (followed topics), and surfaces it as a digest in `wiki/research/digests/`."
metadata:
  hermes:
    category: research
---

# daily-digest

**Trigger**: `/daily-digest` or "morning digest", "what's new today"
**Domain**: research
**Automation**: remote (scheduled 07:00 daily via cron)

## Description
Automated morning briefing. No user input required. Pulls top content from GitHub trending, Hacker News, Twitter/X (followed topics), and surfaces it as a digest in `wiki/research/digests/`.

## Instructions
1. Fetch sources (all in parallel):
   - **GitHub Trending**: Top 10 repos today (language filters: TypeScript, Python, any AI/security).
   - **Hacker News**: Top 15 stories from past 24h.
   - **Twitter/X**: Top threads from tracked accounts/topics (AI, cybersecurity, Next.js, trading).
   - **RSS feeds** (if configured in `domains/research/feeds.json`).
2. Score each item by relevance to user domains: [research, app-dev, cybersecurity, ai-ml, trading, fitness].
3. Format digest:
   - Top 3 items per domain
   - Each item: title, source, one-line summary, link
4. Save to `wiki/research/digests/YYYY-MM-DD.md`.
5. Flag any items that match `deep-research` or `yt-research` for queue (append to `domains/research/queue.md`).

## Input
None (scheduled). Optional override: `/daily-digest --date 2026-05-07` to regenerate past digest.

## Output
```markdown
---
domain: research
date: YYYY-MM-DD
type: daily-digest
---
# Daily Digest — YYYY-MM-DD
## App Dev
## Cybersecurity
## AI/ML
## Trading
## General Tech
## Research Queue (flagged for follow-up)
```

## Automation
**Remote** — GitHub Actions cron:
```yaml
on:
  schedule:
    - cron: '0 7 * * *'
jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - run: Codex --headless --project=. "/daily-digest"
      - run: git add wiki/research/digests/ && git commit -m "digest: YYYY-MM-DD" && git push
```
Config: `domains/research/feeds.json` for custom RSS/Twitter accounts.
