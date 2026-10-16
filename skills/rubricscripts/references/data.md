# RUBRIC Scripts data

Two data sources (AW plan 57): `scripts.json` in the vault folder `Agentic Output/scripts/`, and the operator's state in a per-machine file. The page reads both on every load and when the window gets focus again, so a change you save shows up without a restart. Read and write them only with `scripts/rubric-scripts.js`.

## Contents

`scripts.json` (yours) · `state.json` (the user's) · What the app tidies · Saving and the stale tab

## `scripts.json` (you write it)

```
{ "app": "rubric-scripts", "format": 1, "owner": "<name>",
  "scripts": [ {
    "id":         "rank"                    lowercase letters, numbers and dashes; never change it once the user has comments
    "keyword":    "RANK"                    the comment keyword
    "title":      "..."                     what the card and the page header show
    "tags":       ["AI agents", "SEO"]      1 to 3, the homepage filters by them
    "icon":       "<path .../>"             drawing tags for a 48 x 48 grid, class="a" on the one orange part
    "created":    "2026-09-22T10:00:00"     when you wrote it (Newest sort)
    "updated":    "2026-09-22T18:00:00"     when you last changed it (Last edited sort)
    "hooks":      [ { "id": "h1", "note": "the hook shape", "text": "the opening line or two" }, ... ]   1 to 5, usually 3
    "hook":       "h2"                      the hook you would record; the user's pick in state.json wins
    "body":       "..."                     the rest of the script, paragraphs split by a blank line, no hook
    "caption":    "..."                     the post caption, without a Comment "KEYWORD" first line
    "references": [ { "label": "...", "url": "https://...", "note": "a few words" } ]   a note alone is fine for a fact with no link
    "video":      null                      Week 4
    "channels":   ["tiktok", "instagram", "threads", "youtube-shorts"]   Week 4, shown darkened until then
  } ] }
```

`put scripts.json` runs the check on every write. It names each problem by script and field.

## state (the page writes it; read it with `state`, change it only with `mark-applied`)

```
{ "rev": 7,                                   goes up by 1 on every save; add 1 when you change this file
  "updated": "2026-10-12T05:00:00.000Z",
  "order": ["rank", "modes", "prompts"],      the user's card order (My order)
  "note": "patterns across all scripts",
  "tone": true,                               false = do not update /tone from this hand-off
  "items": {
    "rank": {
      "hook": "h2",                           the hook the user chose
      "note": "a note on this script",
      "comments": [
        { "id": "c...", "region": "hook" | "body" | "caption" | "refs",
          "hook": "h2",                       only when region is "hook": which hook the words are in
          "where": "hook H2",                 the label the user saw
          "quote": "expensive SEO tools",     the exact words they highlighted
          "note": "Name one, like Ahrefs.",   what they want changed
          "at": "2026-10-12T04:58:00.000Z",
          "applied": "2026-10-12" }           you add this after applying it
      ],
      "edits": { "hooks": { "h2": "new hook text" }, "body": "...", "caption": "..." },   only fields the user changed by hand
      "refs": [ { "label": "ahrefs.com", "url": "https://ahrefs.com/pricing", "note": "from US$129 a month" } ],
      "touched": 1760245080000 } } }
```

## What the app tidies

The app never breaks on an odd `scripts.json`: a duplicate id gets a suffix, a caption that starts with `Comment "KEYWORD"` loses that line, a missing `hook` falls back to the first hook. Each fix shows in a yellow line on the homepage, so the user sees what to ask you to correct.

## Saving and the stale tab

Every save from the page sends the `rev` it last saw. If the file moved on (another tab, or you marking comments applied), the server refuses the save, and the page reloads the newer file and asks the user to make their last change again. `mark-applied` adds 1 to `rev` for you.
