---
name: dream-review
description: "Author the overnight Dream Review for an agentic-workspace checkout: read the deterministic signal pack (cost, sessions, memory, skills, workflow), dedup against last night's insights and their statuses, reason through the 8-pillar lens, and emit 0-5 personal, number-backed insights as strict JSON the Dream UI renders, plus a dated markdown digest in the Obsidian vault. No user input required."
metadata:
  hermes:
    category: research
---

# dream-review

> **Mirror file.** The Steps here are kept **identical** to
> `agentic-workspace/.claude/commands/dream.md` (the copy the nightly headless
> run actually loads). Edit both together, or the overnight engine silently
> drifts from this skill.

**Trigger**: `/dream` or "run dream", "overnight insights", "dream review"
**Domain**: research
**Automation**: remote (scheduled overnight via the `dream.schedule` cron in `user-config.json`)

## Description

Author the overnight **Dream Review** — 0–5 personal, specific insights about how the user
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

0. **Freshness gate.** Before anything else, verify `server/data/dream-signal.json` exists
   and its `window.nowISO` is less than 24 hours old. If it is missing or stale, do NOT
   author insights from it — write a single `session`-pillar "engine health" insight instead
   ("Dream signal pack is missing/stale since <date> — the overnight pipeline needs attention",
   with `action: {"kind":"unsupported"}`) and stop. Never invent numbers.
   On `/dream doctor`: only run the checks and report — signal-pack age, `dream-latest.json`
   age vs `dream.schedule.cadence`, vault path resolution, and whether the `dream-review`
   Hermes cron job exists and is active (`hermes cron list`). No insights, no writes.

1. **Read the signal pack** `server/data/dream-signal.json` (built fresh before you run). It
   carries the raw metrics behind each pillar: `cost` (totalUsd, byModel, opusShare, cacheRatio),
   `session` (count, oversized, longestTokens), `memory` (notes, stale, noFrontmatter,
   staleExamples), `skills` (runs, distinct, bySkill), `workflow.sequences`, `external.enabled`,
   `business`/`retrieval` (placeholders), `hints` (deterministic findings — seed ideas), and
   `window` (days, sinceISO, nowISO). Also read the `dream` block of `server/data/user-config.json`.

1b. **Read last night before writing tonight.** Load the previous
   `server/data/dream-latest.json` (if any) and note each prior insight's `pillar`, `title`,
   the numbers it cited, and its `status`:
   - **Never re-emit a semantically matching insight the user `dismissed`** — that is the user saying no,
     even when tonight's date-based `id`, title, or prose differs. The server identifies a match by
     `pillar + action.kind + typed action input`. Re-open it only when its stated impact has at least
     **doubled** (for example, $100/mo → $200/mo); say exactly what crossed that threshold.
   - A repeat of an `open`/`declined` insight is allowed **only if its number moved
     materially** — and the body must say so ("Opus share still 61%, up from 54% last week").
     A daily run over a 7-day window overlaps ~6/7 night-to-night; without this rule,
     repetition is the default output, not the exception.
   - If a prior insight `execution.state` is `succeeded`, check whether its metric actually moved in tonight's
     pack and report the result as evidence — a win is a valid insight.

1c. **Norms file.** Read `server/data/dream-norms.md` if it exists. Each line records
   behavior the user has declared intentional ("session abandonment is deliberate
   exploration"). Never emit an insight criticizing behavior covered by a norm.
   When last night's file shows an insight newly `dismissed`, append one norm line for it:
   `- <YYYY-MM-DD> dismissed: <title> — treat as intentional unless the metric doubles.`
   Create the file on first append.

1d. **Weekly postmortem (Monday runs only).** When `window.nowISO` falls on a Monday, score
   the trail before authoring: read `server/data/dream-archive/dream-latest-*.json` entries
   7–14 days old and their matching archived signal packs. Use execution outcomes, not old button
   labels: `succeeded` is **HIT** only when executor evidence exists *and* the cited metric moved
   in the expected direction; `failed` is **FAILED** (never a hit); `unsupported` is **UNSUPPORTED**
   (a registry/ranking gap, never a hit); `declined` and `dismissed` are **DECLINED** / **DISMISSED**;
   an untouched `proposed` item is **UNATTEMPTED**. A successful action with evidence but no metric
   movement is **EXECUTED, NO EFFECT** — useful evidence, not a hit. Report outcome counts and a
   hit rate whose denominator is only succeeded actions with a measurable expected metric.
   A pillar repeatedly declined/dismissed must not lead tonight's insights; recurring unsupported
   suggestions must be phrased as evidence-only until the registry gains a real safe executor.
   Append one concise ranking-learning entry to `domains/research/learnings.md` when the same
   semantic recommendation is unsupported or dismissed twice (include pillar, action kind, and
   why it was suppressed), so a later registry/ranking change is deliberate. Skip silently if
   the archive is empty (it fills nightly from now on).

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

4. **Emit 0–5 insights** and **write strict JSON** to `server/data/dream-latest.json` using the
   exact schema below — the frontend depends on these keys. Skip pillars with no real signal
   rather than padding: fewer than 3 pillars carrying real, non-repeated signal means fewer
   insights, and a quiet week is a valid result ("Quiet week — 1 improvement found"). Never
   pad to reach a count. Derive `headline` count from the number of insights (no hardcoding).
   Order insights by actionability first, then expected impact (est $ saved + minutes saved): a
   safe supported action with strong evidence outranks an equally-sized unsupported suggestion.
   Do not add a weak insight merely to make Apply available; `0` insights is correct when no
   actionable or worthwhile evidence survives repeat suppression.

   ```json
   {
     "generatedAt": "ISO",
     "refreshedAt": "ISO",
     "windowDays": 7,
     "source": "Claude",
     "headline": "4 improvements found overnight",
     "insights": [{
       "id": "cost-20260803-1",
       "pillar": "cost",
       "pillarLabel": "COST",
       "kicker": "Spend smarter",
       "title": "You're paying Opus prices for jobs Haiku can do",
       "body": "Roughly 60% of yesterday's Opus calls were plain file reads…",
       "why": ["1.4M of 2.3M Opus tokens were file reads", "Haiku scored identically last month"],
       "action": { "kind": "direct.cost-review" },
       "estSavingUsdPerMo": 348,
       "minutesSaved": 0,
       "evidence": "observed",
       "confidence": "high",
       "status": "open"
     }]
   }
   ```

   Field rules:
   - `id`: `<pillar>-<YYYYMMDD>-<n>` (date from `window.nowISO`), unique **across runs** — the
     server preserves per-insight status by id, so a reused id (`cost-1`) silently grafts an
     old insight's apply/dismiss state onto a new, unrelated one.
     `pillar`: one of the 8 lens ids. `pillarLabel`: uppercased.
   - `kicker`: short imperative (e.g. "Sharpen your memory"). `title`: bold one-liner.
   - `body`: 1–3 sentences of prose with specifics from the pack.
   - `why`: 1–3 short evidence bullets (the numbers behind the call).
   - `action`: optional. It may contain only a registry `kind` and its declared structured
     `input`; never emit a shell command, path, URL, prompt, endpoint, or author-supplied
     executor/label/risk/summary. The initial allowed kinds are `direct.cost-review`,
     `operator.create-task` with `input: {"taskType":"review-cost-anomaly"}`, and
     `unsupported`. Choose a supported kind only when the signal pack provides every required
     typed input and the proposed work is within that kind's fixed contract; otherwise use
     `null` or `{ "kind": "unsupported" }` (including session compaction). A display-only `investigate` note may contain a
     suggestion, but it is never an action payload.
   - `estSavingUsdPerMo` / `minutesSaved`: integers, best estimate, `0` if unknown.
   - `evidence`: `"observed"` (directly counted in the signal pack) or `"inferred"`
     (pattern guess). `confidence`: `"high"` / `"med"` / `"low"`. Only an
     observed + high insight may carry `estSavingUsdPerMo` > 0 — an inferred saving
     estimate is a made-up number.
   - `status`: always `"open"` for new insights. The server adds `execution`; never author
     `applied` or `skipped` (old values are display-only history).

5. **Append a human digest** to the connected Obsidian vault at
   `<vault>/Agentic Output/digests/dream-YYYY-MM-DD.md` (date from the window's `nowISO`):
   a short markdown summary of the insights for the vault record. This is the same path the
   deterministic engine's `writeDigest()` uses (`agenticOutputDir('digests')`), so the two halves
   land side by side. Resolve `<vault>` via `$AGENTIC_VAULT`, then `vaultPath` in
   `server/data/user-config.json`. If no vault resolves, skip the digest — never write into the
   repo. Announce the full vault path in chat when writing.

6. **Log the run.** Append one line to `domains/research/learnings.md` in the workspace:
   date, insight count, pillars used, and anything the signal pack couldn't tell you
   (dead pillars, suspected ranking misses). The server logs the run itself to
   `server/data/runs.json` — do not double-write that file.

7. Keep it tight and personal. The user reads this as a morning briefing.
