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

4. **Log the run**: append ONE object to the JSON array in
   `server/data/runs.json` in the agentic-workspace checkout if one is present,
   using exactly these field names (the workspace stats page reads
   `timestamp`; other names like `startedAt` break it):
   ```json
   {
     "skill": "insights-recon",
     "date": "<digest date, YYYY-MM-DD>",
     "timestamp": "<real current UTC time, ISO 8601, e.g. 2026-10-11T19:02:36.603Z — from `date -u +%FT%T.%3NZ`, never a made-up midnight>",
     "status": "ok | error",
     "notes": "<one paragraph: what the day looked like, anything odd>"
   }
   ```
   Then note anything learned (dead source, ranking miss) in
   `domains/content/learnings.md`.

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

**Excluded by choice, not oversight.** Reddit, X, TikTok, YouTube comments,
Bluesky, and the `last30days` skill. The user chose credible sources over
engagement volume: a curated pool of vendor announcements and high-signal
curators beats a wider net that dilutes it. This means the urgency gate sees
social virality only through HN, and that trade is intentional. HN stays
because its front page signals what builders care about rather than raw
engagement.

Do not add these sources or re-pitch them as a routine suggestion. **Do** flag
it in the Gaps section if you observe a specific major story the curated pool
missed and social caught first — that is evidence, not a proposal.

## Boundaries

- Never draft a full post here. That is `insights-draft`.
- Vault writes only under `Agentic Output/insights/`.
- Changing the source list means noting it in `domains/content/learnings.md`.

<!-- BEGIN brief-v2 -->
## Output format: brief-v2 (overrides any earlier format guidance in this skill)

Write the note in the brief-v2 shape the Agentic Workspace `/brief` reader
renders as cards (full spec: `deploy/briefs/NEWS-FORMAT.md` in the
agentic-workspace repo).

- Frontmatter: keep the existing keys and add `format: brief-v2` and `agent: <you>`, where `<you>` is `claude`, `codex` or `hermes`, whichever agent is writing.
- Right under every `## <Section>` heading, add the line `<!-- agent: <you> -->`.
- Open each section with `> [!tldr] <one sentence, ≤30 words, one ==highlight== on the takeaway>`.
- Inside each `### <Group>`, write every story as:

  ```
  #### <plain headline, ≤14 words, no bold; in Top Headlines, Emerging and AI news stories wrap the outcome (2–6 words) in ==…==>
  - tldr: <≤25 words, no highlight>
  - key: <≤20 words, the one number/name/date in **bold**>   (1–3 of these)
  - why: <≤20 words, why it matters to a small-business owner; omit if nothing real>
  - src: [Source](url) · [Source](url)
  ```
- Use at most 5 Top Headlines and 4 Emerging stories per section. Keep Source Health / Gaps as short bullets.
- Tone / Sentiment: put `<!-- mood: good|bad|mixed -->` on the line under the heading, then 1–2 sentences that open with a bold mood line of 2–10 words, e.g. `**A heavier day than most**, led by …`.
- Highlights mark the outcome only, meaning what happened or was decided. Use exactly one `==…==` per Top Headlines, Emerging and AI news story, in the headline, and never a whole sentence. Other groups get no highlight.
- Write one file per date, as now. Never rewrite or delete a previous date's note.
<!-- END brief-v2 -->
