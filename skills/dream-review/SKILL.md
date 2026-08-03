---
name: dream-review
description: "Author the overnight Dream Review for an agentic-workspace checkout: read the deterministic signal pack (cost, sessions, memory, skills, workflow), reason through the 8-pillar lens, and emit 3-5 personal, number-backed insights as strict JSON the Dream UI renders, plus a dated markdown digest in the Obsidian vault. No user input required."
metadata:
  hermes:
    category: research
---

# dream-review

**Trigger**: `/dream` or "run dream", "overnight insights", "dream review"
**Domain**: research
**Automation**: remote (scheduled overnight via the `dream.schedule` cron in `user-config.json`)

## Description

Author the overnight **Dream Review** — 3–5 personal, specific insights about how the user
actually uses AI, reasoned through the **8-pillar lens**. You are the engine; "Dream" is the
feature. Be concrete: cite the real numbers from the signal pack, never generic advice.

## Prerequisites (host-bound skill)

This skill is **not standalone** — it is the LLM half of the Dream engine in an
**agentic-workspace** checkout. It requires:

- `server/dream/` (deterministic dimension scoring) and a running/recently-run
  `POST /api/dream/run`, which builds `server/data/dream-signal.json` fresh before you run.
- `server/data/user-config.json` with a `dream` block (`webSearch`, `schedule`).
- The Dream frontend, which reads `server/data/dream-latest.json` by exact key.

Resolve the workspace root in this order:
1. `$AGENTIC_WORKSPACE` env var, if set.
2. Known paths: `/opt/agentic/workspace` (VPS),
   `C:\Users\pawar\ai-workspace\claude-projects\agentic-workspace` (laptop).
3. The current repo, if it contains `server/dream/index.js`.

If no workspace resolves, say so and stop — do not invent a signal pack.

## Steps

1. **Read the signal pack** `server/data/dream-signal.json` (built fresh before you run). It
   carries the raw metrics behind each pillar: `cost` (totalUsd, byModel, opusShare, cacheRatio),
   `session` (count, oversized, longestTokens), `memory` (notes, stale, noFrontmatter,
   staleExamples), `skills` (runs, distinct, bySkill), `workflow.sequences`, `external.enabled`,
   `business`/`retrieval` (placeholders), `hints` (deterministic findings — seed ideas), and
   `window` (days, sinceISO, nowISO). Also read the `dream` block of `server/data/user-config.json`.

2. **Analyze through the 8-pillar lens** — this is *how Dream thinks*, not UI:
   - **cost** — model mix, Opus over-use, cache reuse → routing/savings opportunities.
   - **session** — oversized/long sessions → compaction, splitting.
   - **memory** — stale notes, missing frontmatter → vault hygiene.
   - **skills** — which skills run, which are dormant → activation/ROI.
   - **workflow** — repeated adjacent skill sequences → automation candidates.
   - **external** — model/pricing/tooling news (only if web search enabled below).
   - **business** — downstream value (skip unless the pack carries signal).
   - **retrieval** — retrieval quality (skip unless the pack carries signal).

3. **Web search gate.** If `external.enabled` is `true` (mirrors `dream.webSearch`), you MAY
   web-search for relevant model/pricing/tooling news and emit an `external` insight. If it is
   `false`, do **not** web-search at all.

4. **Emit 3–5 insights** and **write strict JSON** to `server/data/dream-latest.json` using the
   exact schema below — the frontend depends on these keys. Skip pillars with no real signal
   rather than padding. Derive `headline` count from the number of insights (no hardcoding).

   ```json
   {
     "generatedAt": "ISO",
     "refreshedAt": "ISO",
     "windowDays": 7,
     "source": "Claude",
     "headline": "4 improvements found overnight",
     "insights": [{
       "id": "cost-1",
       "pillar": "cost",
       "pillarLabel": "COST",
       "kicker": "Spend smarter",
       "title": "You're paying Opus prices for jobs Haiku can do",
       "body": "Roughly 60% of yesterday's Opus calls were plain file reads…",
       "why": ["1.4M of 2.3M Opus tokens were file reads", "Haiku scored identically last month"],
       "action": { "label": "TRY IT NOW — PASTE THIS INTO CLAUDE CODE", "snippet": "claude -p \"/route-reads haiku\"" },
       "estSavingUsdPerMo": 348,
       "minutesSaved": 0,
       "status": "open"
     }]
   }
   ```

   Field rules:
   - `id`: `<pillar>-<n>`, unique. `pillar`: one of the 8 lens ids. `pillarLabel`: uppercased.
   - `kicker`: short imperative (e.g. "Sharpen your memory"). `title`: bold one-liner.
   - `body`: 1–3 sentences of prose with specifics from the pack.
   - `why`: 1–3 short evidence bullets (the numbers behind the call).
   - `action`: optional — include only when there's a concrete command to paste; else `null`.
   - `estSavingUsdPerMo` / `minutesSaved`: integers, best estimate, `0` if unknown.
   - `status`: always `"open"` for new insights.

5. **Append a human digest** to the connected Obsidian vault at
   `<vault>/Agentic Output/digests/dream-YYYY-MM-DD.md` (date from the window's `nowISO`):
   a short markdown summary of the insights for the vault record. This is the same path the
   deterministic engine's `writeDigest()` uses (`agenticOutputDir('digests')`), so the two halves
   land side by side. Resolve `<vault>` via `$AGENTIC_VAULT`, then `vaultPath` in
   `server/data/user-config.json`. If no vault resolves, skip the digest — never write into the
   repo. Announce the full vault path in chat when writing.

6. Keep it tight and personal. The user reads this as a morning briefing.
