---
name: carousels
description: "Makes and revises Instagram carousels for RUBRIC Carousels, the /carousels page in Agentic Workspace, where the operator reviews every carousel at once: pins comments on cards, approves cards, picks the cover and reorders. Makes a new carousel folder from the template, writes its deck.js (cards, caption, drawings), makes the snapshots, and applies the operator's review. Use when the operator says '/carousels', 'make a carousel', 'new carousel about', 'apply my carousel comments', 'redo the carousel snapshots', 'mark the carousel live', or pastes comments copied from RUBRIC Carousels."
argument-hint: "[topic for a new carousel | apply <slug> | snapshots <slug> | status <slug> <draft|ready|scheduled|live>]"
metadata:
  hermes:
    category: creative
---

# RUBRIC Carousels (Agentic Workspace)

You write the carousels; the `/carousels` page shows them; the operator reviews; you apply
the review. The page has no AI inside. Adapted from RUBRIC Carousels by Jay E |
RoboNuggets (MIT) for Agentic Workspace plan 66.

<!-- YOUR DEFAULTS: change these values here, in one place. -->
- Page: `/carousels` in Agentic Workspace (Command Centre, Micro Apps, RUBRIC Carousels)
- CLI: `node "$AW/scripts/carousels.js"` where `$AW` is `$AW_REPO`, else `/root/agentic-workspace`, else the current repo if it holds that file.
- Carousels: `~/Documents/Hermes/carousels/<slug>/` (print the folder with `paths`)
- Cards per carousel: 10 at most, the cover included (Instagram's limit)
- Voice for card text and captions: the /tone skill
<!-- END YOUR DEFAULTS -->

## CLI

```
carousels.js paths              the carousels folder and _template/
carousels.js list               slug, cards, open comments, status; "snapshots out of date" when deck.js is newer
carousels.js new <slug>         a new folder with deck.js + index.html from _template/
carousels.js review <slug>      review.json: cover pick, approvals, order, comments
carousels.js snapshots <slug>   makes export/ (card PNGs, thumbs, manifest.json) with Camoufox
```

## A carousel folder

```
<slug>/
  deck.js        everything about this carousel: the one file you write
  index.html     the card engine: copied by `new`, never edited
  cover/         optional cover images (1080 x 1350 PNG, keep the top third empty for the title)
  items/         optional pictures or clips the cards use
  export/        snapshots, made by `snapshots`, never by hand
  review.json    the operator's review, written only by the page
  status.json    optional: { "status": "draft|ready|scheduled|live", "at": "...", "url": "https://..." }
```

`deck.js` sets `window.DECK`. Every field is explained in the comments of
`_template/deck.js`; read them before writing one. Drawings are small functions in
`scenes`, on a 540 x 675 canvas, with the top third kept clear for the title.

## Workflow A: a new carousel

1. Pick a slug (lowercase, dashes) and run `new <slug>`.
2. Write `deck.js`: the cover card, the content cards, a save or follow card, the caption
   (with a comment keyword when there is a giveaway) and the scenes. Write the words with
   /tone. Never use em dashes.
3. Run `snapshots <slug>`. If a card fails to render, the error names it: fix `deck.js`
   and run it again.
4. Tell the operator in 2 lines: the slug, the card count, and that it is on the
   Carousels page for review.

## Workflow B: apply a review

1. `review <slug>` (or the comments the operator pasted). Card numbers are indexes in
   `cards`, from 0. `target` is `<slug>#<index>`; `x`/`y` are the pin in percent.
2. Leave approved cards alone. Make each comment's change in `deck.js` (or swap the
   cover image). If `order` changed, reorder `cards` to match. Use the picked `cover`
   as `coverDefault`.
3. Run `snapshots <slug>` so the page shows the new cards.
4. Never edit `review.json`: the page marks comments applied itself after an Apply run.
   When you worked from pasted comments, say which ones you applied.
5. Never edit anything outside that carousel's folder.

## Workflow C: status

Write `status.json` when the operator says it is ready, scheduled or live. Nothing here
posts anything.
