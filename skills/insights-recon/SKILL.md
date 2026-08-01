---
name: insights-recon
description: "Daily AI-news recon for the guidantoperations.tech Insights blog. Sweeps 13 sources (vendor RSS, curators, TLDR/smol.ai, HN, HF/GitHub trending), dedupes against a 21-day window, ranks for a business-reader audience, and writes a vault digest with an urgency flag, content/business gaps, and 2-3 opinionated teaser candidates. No user input required."
metadata:
  hermes:
    category: content
---

# insights-recon

**Trigger**: `/insights-recon` or "run insights recon", "daily AI news sweep"
**Domain**: content
**Automation**: remote (scheduled ~07:00 daily via Hermes cron, delivers to Telegram)

## Description

Daily recon for the guidantoperations.tech "Insights" blog. Fetch the wide-net
sources, rank what matters for the audience (business leaders and builders
adopting AI agents/ops), write the vault digest, and surface 2-3 opinionated
teaser candidates. Posting cadence is 3x/week; recon is daily because the
industry moves faster than the publishing schedule.

Companion skill: `insights-draft` turns a picked teaser into a published post.

## Arguments

`/insights-recon [--date YYYY-MM-DD]` (default: today)

## Output location (resolve first)

Digest goes to the connected Obsidian vault so it syncs to every device.
Resolve the vault path in this order:
1. `$AGENTIC_VAULT` / `$CLAUDE_VAULT` env var, if set.
2. Known paths: `/opt/agentic/obsidian/vault` (VPS),
   `C:\Users\pawar\Documents\ajqcd-zaozt` (laptop), `~/Documents/ajqcd-zaozt`.
3. `vaultPath` in `server/data/user-config.json` of an agentic-workspace checkout.

Digest path: `<vault>/Agentic Output/insights/<date>.md`.
If no vault resolves, print the digest to the user instead. Never guess a path.
Announce the full vault path in chat when writing.

Raw fetch output goes to `$INSIGHTS_DATA_DIR` or `~/.insights/` (not the vault).

## Steps

1. **Fetch**: run `node insights-recon.mjs` from this skill directory.
   Writes `raw-<date>.json` with `stories[]`, `urgentCandidates[]`, and
   `errors{}`. Source failures are non-fatal: report them in the digest
   footer, never abort the run.

2. **Read + rank** the raw stories. Scoring priorities, in order:
   - Relevance to the audience: AI agents, AI ops, enterprise adoption, model
     releases, strategy/governance shifts, tooling that changes how businesses
     ship AI. Down-rank pure research papers, consumer gadget news, hype.
   - `crossSourceHits > 1` (multiple independent sources agree it matters).
   - Tier weight: primary (vendor) > curator > aggregate > social > ship.
   - Anthropic titles are scraped from HTML and arrive with category/date
     prefixes mashed in. Clean them.

3. **Write the digest**:

   ```markdown
   ---
   title: AI Insights Recon <date>
   description: Daily AI-news sweep with teaser candidates
   tags: [insights, recon]
   ---
   # AI Insights — <date>

   ## ⚡ Urgent
   ONLY when something clears the gate — omit the section entirely on normal
   days (most days). Mechanical side is precomputed in `urgentCandidates`:
   3+ cross-source hits within the window, OR HN >=400 points. You may also
   promote a frontier-lab release or breaking policy move the numbers cannot
   see yet. Every entry needs a one-line justification of why it is genuinely
   urgent for Guide's positioning (viral moment, competitor window, market
   shift). If you cannot write that line honestly, demote it to Stories. The
   flag must stay rare or it becomes noise.

   ## TL;DR
   3-5 bullets: the day in AI, one line each.

   ## Stories
   Grouped by theme (Releases / Business & adoption / Safety & governance /
   Tooling). Each: **[Title](url)** plus 1-2 sentences of summary and why it
   matters for the audience. Max ~15 stories. Skip filler.

   ## Teaser candidates
   ### 1. <working title>   (ranked, best first)
   - **Angle:** the opinionated take (a stance, not a summary)
   - **Sources:** links
   - **Teaser:** 2-3 sentences in Guide's voice. No em dashes, no invented
     aphorisms — see insights-draft for the full voice rules.
   ### 2. ...
   (2-3 candidates. Only stories that can carry a full opinionated post.)

   ## Gaps
   Content gap (daily): the story everyone is covering but nobody is angling
   for business readers — the piece Guide could publish first. 1-2 max, each
   with the specific unserved angle. Skip the section if there is no honest
   gap today; do not force one.
   Business gap (Mondays only): recurring pain visible across the week's
   community chatter that maps to a plausible Guidant service offering. Frame
   it as a hypothesis with evidence links and flag it clearly as a bet — it
   could be a gamechanger or a flop. The user takes that risk; the job is to
   surface it with the reasoning visible.

   ## Source health
   Failed sources from `errors`, or "all green".
   ```

4. **Log the run**: append to `server/data/runs.json` in the agentic-workspace
   checkout if one is present, and note anything learned (dead source, ranking
   miss) in `domains/content/learnings.md`.

5. **Deliver** (only when running under Hermes cron with a delivery channel):
   send the TL;DR and the teaser titles/angles to Telegram. If the digest has
   an Urgent section, the message MUST open with `⚡ URGENT` and those items
   before anything else, so an urgent day is distinguishable at a glance.
   Reply format for picking: "draft 2" or "draft <title>".

## Sources

13 sources across 5 tiers, defined in `insights-recon.mjs`:
primary (OpenAI, Anthropic, DeepMind, Google AI, Mistral) ·
curator (Simon Willison, Import AI) · aggregate (TLDR AI, smol.ai) ·
social (HN front page via Algolia) · ship (HF blog, HF trending, GH trending).

Known-dead feeds, do not re-add: `ai.meta.com/blog/rss` (no RSS exists),
`bensbites.beehiiv.com/feed` (404), `hnrss.org` (unreliable — use Algolia).

**Deliberately excluded — do not propose adding these.** Reddit, X, TikTok,
YouTube comments, Bluesky, and the `last30days` skill. The user chose credible
sources over engagement volume: a curated pool of vendor announcements and
high-signal curators beats a wider net that dilutes it. This means the urgency
gate sees social virality only through HN, and that trade is intentional. HN
stays because its front page is a signal about what builders care about, not a
raw engagement metric.

## Boundaries

- Never draft a full post here. That is `insights-draft`.
- Vault writes only under `Agentic Output/insights/`.
- Changing the source list means noting it in `domains/content/learnings.md`.
