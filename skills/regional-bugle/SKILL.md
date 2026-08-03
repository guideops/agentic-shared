---
name: regional-bugle
description: "Create a country/region-specific daily news brief in English and save it to the connected Obsidian vault. Companion to daily-bugle (which is global-only). Use when the user asks for news about a specific country or region — e.g. 'thailand news', 'what's happening in the UK', 'NZ brief', 'regional bugle', '/regional-bugle <country>' — or wants a local/national briefing rather than a global one. Pulls credible local sources (including local-language outlets) but always writes the brief in English. If no region is given, asks which region; defaults to New Zealand."
metadata:
  short-description: Country-specific news brief in English; local-language sources OK, output English only
---

# Regional Bugle

Produce a concise national/regional briefing in English for one country per run.
Companion to `daily-bugle`: that skill is global-only; this one is country-focused.

## Region resolution (do this first)
1. **Inline argument** (`/regional-bugle thailand`, "regional bugle for south korea"): use it. Normalize to the kebab-case pack names in `packs.md` (e.g. "UK", "Britain" → `united-kingdom`; "korea" → `south-korea`).
2. **No region given, interactive session**: ask one question — "Which region?" — offering the packs currently in `packs.md` plus "somewhere else". Do not ask anything beyond the region.
3. **No region given and no answer possible** (cron/headless): default to `new-zealand`.

## Sources
1. Read `packs.md` in this skill directory and use the pack for the resolved region.
2. Sweep every feed in the pack. Use web search only to *expand* a story the sweep surfaced or to fill a visible gap, not as primary discovery.
3. A story needs a `wire` or `daily` tier source before it goes in Top Headlines; `indie`-only or aggregator-only items belong in Emerging at most.
4. Source failures are non-fatal: note them in the Source Health footer and keep going. If a feed fails on 3+ consecutive runs, move it to the **Known-dead** list in `packs.md` with the date.

### Fallback mode (region has no pack)
When the resolved region is not in `packs.md`:
1. Discover sources: the country's national wire service or public broadcaster, 1–2 major dailies, and one credible English-language outlet covering the country (BBC/Reuters country page counts). Credibility bar: established newsroom with editorial standards — no content farms, no state propaganda outlets presented as independent, no engagement-driven aggregators.
2. Verify each candidate feed actually returns RSS/Atom (fetch it) before using it.
3. Write the brief, flagging it at the top: `> First run for this region — sources auto-discovered, not yet reviewed.`
4. Append the new pack to `packs.md` with status `auto`, and add any dead candidates to Known-dead. Next run for that region is then instant.

## Language and translation
- Pull local-language sources freely; **all output prose is English, always**.
- Translate faithfully: keep the claim, attribution, and hedging of the original — do not sharpen a "reportedly" into a fact or flatten nuance for brevity.
- Mark items whose only source is local-language: append *(translated from Thai — Thairath)* etc. to the bullet.
- Use standard English romanizations for names and places (Revised Romanization for Korean, RTGS for Thai); on first mention of a lesser-known name, include the original script in parentheses if it aids searching.
- If a local-language story is significant, check whether an English-language credible outlet has it too and prefer citing both.
- Never present a machine-mangled translation; if the meaning is uncertain, say what is confirmed and note the uncertainty.

## Continuity (read before writing)
Before drafting, read the last 3 regional-bugle notes *for the same region*.
- A story already covered reappears only if it materially changed; lead with what changed and link the prior note.
- Prior **Emerging** items get one of three fates: promote (now a headline), carry (still building — say what moved), or drop silently.
- One clause of context plus the update; no daily re-telling of running stories.

## Writing rules
- Concise, neutral, newsroom-like. National focus: what matters *in and to* this country, including how global stories land locally.
- Do not pad with global news that has no specific local angle — that is daily-bugle's job.
- If little happened, say so directly; a quiet day is a valid report.

## Output format
One markdown note per region per day; later same-day runs append an **Update** section to the same file:

```markdown
---
date: YYYY-MM-DD
type: regional-bugle
region: <kebab-name>
---
# Regional Bugle — <Region> — YYYY-MM-DD

## Top Headlines
- ...

## Emerging / Gaining Attention
- ...

## Global Stories, Local Angle
- ... (omit if none today)

## Tone / Sentiment
- ...

## Update (HH:MM)        <!-- only on second+ run of the day -->
### What Changed
- ...

## Sources
- ...

## Source Health
- Failed feeds this run (or "all green")
```

## Obsidian output
- Resolve the connected vault path the same way daily-bugle does; never guess a path, and announce the full path when writing.
- Note path: `Agentic Output/digests/regional/<region>/YYYY-MM-DD.md`.
- After writing on Unix/Linux, set mode `0644` (and owner/group to match the parent folder when permitted) so Syncthing can read it, and verify with `stat`.

## Boundaries
- One region per run; for several regions, run the skill once each.
- Global brief requests go to `daily-bugle`, not here.
- Vault writes only under `Agentic Output/digests/regional/`.
- Pack edits (`packs.md`) only via fallback mode or explicit user request.
