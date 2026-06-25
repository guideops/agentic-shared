---
name: daily-digest
description: "Automated morning briefing. No user input required. Pulls top content from GitHub trending, Hacker News, Twitter/X (followed topics), and surfaces it as a digest in the connected Obsidian vault under `Agentic Output/digests/`."
metadata:
  hermes:
    category: research
---

# daily-digest

**Trigger**: `/daily-digest` or "morning digest", "what's new today"
**Domain**: research
**Automation**: remote (scheduled 07:00 daily via cron)

## Description
Automated morning briefing. No user input required. Pulls top content from GitHub trending, Hacker News, Twitter/X (followed topics), and surfaces it as a digest in the connected Obsidian vault under `Agentic Output/digests/`.

## Output location (resolve first)
All automated output goes to the **connected Obsidian vault**, so it syncs to the user's other devices. Resolve the vault path in this order:
1. `$AGENTIC_VAULT` env var, if set.
2. The `vaultPath` value in the agentic-workspace app config `server/data/user-config.json` (try `/root/agentic-workspace/server/data/user-config.json`, then `./server/data/user-config.json`).
3. Fallback: the repo's `vault/` directory.

Write to `<vault>/Agentic Output/digests/` (create the folder if missing). Do **not** write digests into the repo `vault/wiki/...` anymore.

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
4. Save to `<vault>/Agentic Output/digests/YYYY-MM-DD.md` (vault resolved per "Output location" above).
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
      # Output lands in the connected Obsidian vault (Agentic Output/digests/) and
      # syncs via Syncthing — no git commit of digests needed.
```
Config: `domains/research/feeds.json` for custom RSS/Twitter accounts.
