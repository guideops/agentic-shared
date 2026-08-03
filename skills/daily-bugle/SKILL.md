---
name: daily-bugle
description: "Create a twice-daily global news brief in English with morning and afternoon sections, current headlines, emerging topics, overall sentiment/tone, and on-this-day-in-history, then save it to the connected Obsidian vault. Use for globally significant news of any geography: worldwide developments, region-specific, country-specific, or city-specific stories when they are broadly important or widely worth knowing. Do not use for narrowly local or personal-interest regional briefings. Use when the user asks for a global daily brief, morning brief, afternoon update, headlines, what’s making news, what’s the talk, sentiment summaries, or a markdown note written to Obsidian."
metadata:
  short-description: Global news brief with morning/afternoon updates, sentiment, and history
---

# Daily Bugle

Produce a concise global briefing in English.

## Scope
- Focus on *global* news only.
- Do not use this skill for region- or city-specific briefs.
- Prioritize headlines, emerging stories, and items gaining broad attention.
- Include a short overall tone/sentiment read: optimistic, cautious, tense, mixed, etc.
- Include a brief **On this day in history** section.
- If the user asks for an afternoon update, emphasize what is new or materially changed since the morning brief.

## Workflow
1. Read the last 3 daily-bugle notes for continuity (see **Continuity** below).
2. Sweep the named sources below; identify the main headlines and any emerging storylines with broad significance.
3. Summarize the public conversation and overall sentiment in plain English.
4. Add 3–5 notable items from **On this day in history**.
5. Write the final result to the connected Obsidian vault as markdown, including the **Source Health** footer.

## Sources

Sweep this named pool every run. Use web search only to *expand* a story the sweep surfaced (or fill a visible gap), not as the primary discovery method.

- **Wires / primary**: Reuters World (reuters.com/world), AP World (apnews.com/hub/world-news)
- **Broadcasters**: BBC World (`feeds.bbci.co.uk/news/world/rss.xml`), Al Jazeera (`aljazeera.com/xml/rss/all.xml`)
- **Quality dailies**: The Guardian World (`theguardian.com/world/rss`)
- **Discovery / aggregate**: Wikipedia Current Events portal (`en.wikipedia.org/wiki/Portal:Current_events`) — discovery only; verify against a wire before reporting as a headline
- **On this day**: Wikipedia On This Day (`en.wikipedia.org/wiki/Wikipedia:On_this_day/Today`)

Rules:
- A story needs a wire or broadcaster source before it goes in Top Headlines; aggregator-only items belong in Emerging at most.
- Source failures are non-fatal: note the failed source in the Source Health footer and keep going. Never abort the run over one dead source.
- If a source fails on 3+ consecutive runs, list it under **Known-dead** below (with date) so future runs stop retrying it. Known-dead: none yet.
- Call Firecrawl only when the skill needs cleaner extraction or page retrieval.
- Do not invent coverage; if a topic is under-covered, say so.
- Keep all final prose in English even when source material is in another language.

## Continuity (read before writing)

Before drafting, read the previous 3 daily-bugle notes in the digests folder.

- A story already covered reappears only if it materially changed; lead with what changed and link the prior day's note.
- Every item listed under **Emerging** in prior notes gets one of three fates: **promote** (now a headline), **carry** (still building — say what moved), or **drop silently** (fizzled; it gets scored in the weekly look-back, not re-litigated daily).
- Do not restate a running story's full background each day; one clause of context plus the update is enough.

## Weekly look-back (Sunday morning run only)

Add a short `## Week in Review` section to Sunday's morning brief:
- 3–5 lines: the week's defining stories.
- Score last week's Emerging calls: how many promoted to headlines, how many fizzled. One line, honest counts. This is the feedback loop that keeps the Emerging section calibrated rather than speculative.

## Change definition
Treat "change" as any meaningful update since the previous run, including:
- new emerging stories
- updates to existing headlines
- developments in previously reported items
- shifts in sentiment or public attention
- no material change at all, which is still a valid report

For the afternoon update, report what changed if anything; if little changed, say so clearly and still produce the brief.

## Writing rules
- Keep the tone concise, neutral, and newsroom-like.
- In the morning section, establish the baseline.
- In the afternoon section, avoid restating the morning brief unless a story materially changed.
- When there is little change, say that directly rather than forcing new items.
- Keep the note readable as a daily record, not a stream of disconnected bullets.

## Output format
Write a *single daily markdown note* for each date, and append the afternoon update to the same file:

```markdown
---
date: YYYY-MM-DD
type: daily-bugle
scope: global
---
# Daily Bugle — YYYY-MM-DD

## Morning Brief
### Top Headlines
- ...

### Emerging / Gaining Attention
- ...

### Tone / Sentiment
- ...

### On This Day in History
- ...

## Afternoon Update
### What Changed Since Morning
- ...

### New / Emerging Items
- ...

### Updated Tone / Sentiment
- ...

## Reference Links
- Links to any companion notes created during the run (source clips, expansion notes, or related context notes), plus any prior daily-bugle note explicitly used for comparison.
- Prefer Obsidian wiki links when the note lives in the same vault, e.g. `[[2026-06-27 - source - Reuters - Middle East escalation]]`.
- If no companion notes were created, include the most relevant source/article links directly in this section.

## Sources
- ...

## Source Health
- Failed sources this run (or "all green")
```

## Obsidian output
- Resolve the connected vault path before writing.
- Use the connected Obsidian vault, not a repo-local note store, unless the user explicitly says otherwise.
- Prefer a path like `Agentic Output/digests/YYYY-MM-DD.md` or a similar `Agentic Output/` subfolder.
- Create the daily note on the morning run.
- Append the afternoon section to that same day's file on the afternoon run.
- Keep morning and afternoon sections in the same daily note.
- Do not move the note to a different vault subfolder to fix sync issues; first verify the resolved vault path and file permissions.
- After creating or appending the note on Unix/Linux, make it Syncthing-readable:
  - set the note mode to `0644`;
  - when permitted, set the note owner/group to match the parent digest folder;
  - verify with `stat` that Syncthing can read the file.

## When to extend
- Add a separate regional brief skill later for country/city-specific requests.
- Keep this skill global-first so it stays reliable.
- Next upgrade candidate: a small fetch script in this skill directory that pulls the RSS feeds in parallel and dedupes by URL before the model sees them (the tech-digest / insights-recon.mjs pattern), so runs get faster and cheaper.
