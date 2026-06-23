---
name: article-writer
description: "Generate a full-length article or newsletter from a topic prompt. Draws from `wiki/` vault for supporting evidence. Outputs draft to `domains/content/drafts/` and optionally publishes to GitHub Pages or Substack API."
metadata:
  hermes:
    category: content
---

# article-writer

**Trigger**: `/article-writer <topic>` or "write an article about", "draft blog post", "write newsletter"
**Domain**: content
**Automation**: local (on-demand) + remote (scheduled newsletter)

## Description
Generate a full-length article or newsletter from a topic prompt. Draws from `wiki/` vault for supporting evidence. Outputs draft to `domains/content/drafts/` and optionally publishes to GitHub Pages or Substack API.

## Instructions
1. Accept topic + optional format flag (`--format article|newsletter|blog`).
2. Search `wiki/` for relevant notes via Dataview query or file search. Extract supporting facts, quotes, sources.
3. Outline structure:
   - Hook (compelling opening)
   - Context / background
   - Main argument (3-5 sections)
   - Evidence from vault
   - Practical takeaways
   - CTA / closing
4. Write full draft (~800-1500 words for article, ~500 for newsletter).
5. Self-review: check factual claims against vault sources, flag unsupported claims.
6. Save to `domains/content/drafts/YYYY-MM-DD-<slug>.md` with frontmatter.
7. Ask user: "Publish now or save as draft?"
   - If publish → GitHub Pages: commit to `docs/` + push, or Substack: POST via API.
8. Log to `domains/content/learnings.md` + `eval.json`.

## Input
- Topic string (required)
- Optional: `--format article|newsletter` (default: article)
- Optional: `--length short|standard|long` (default: standard)
- Optional: `--publish github|substack|draft` (default: draft)

## Output
```markdown
---
domain: content
date: YYYY-MM-DD
title: <Article Title>
format: article
status: draft|published
publish_url: <URL if published>
summary: <one-line>
tags: [tag1, tag2]
---
# <Title>
<Full article content>
```
Saved to: `domains/content/drafts/YYYY-MM-DD-<slug>.md`
Published to: GitHub Pages `docs/` or Substack API

## Automation
Remote (weekly newsletter): GitHub Actions cron → trigger `article-writer` with rotating topic from `domains/content/topic-queue.md` → auto-publish to Substack.
Config: `domains/content/publish.json` (API keys, targets).
