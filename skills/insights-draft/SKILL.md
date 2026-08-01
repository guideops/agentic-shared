---
name: insights-draft
description: "Turn a picked teaser from an insights-recon digest into a publish-ready post for guidantoperations.tech. Two phases gated by user approval: draft the prose first (outline, opinionated take, strict anti-AI-slop voice rules), then only after approval generate the card image with gpt-image-2 and wire it into the site repo on a review branch."
metadata:
  hermes:
    category: content
---

# insights-draft

**Trigger**: `/insights-draft <date> <pick>` or "draft 2", "draft <teaser title>"
**Domain**: content
**Automation**: local/remote on-demand — needs the site repo and Codex CLI on the
same machine. Both exist on the VPS and the laptop.

## Description

Turn a picked teaser from a recon digest into a publish-ready post. Two phases,
gated by user approval: draft the prose first, and only after the user says the
draft is good, generate the image and wire it into the site. This ordering
exists because the first run burned an image generation on prose that was then
rejected.

## Arguments

`/insights-draft <date> <pick>` — e.g. `/insights-draft 2026-08-02 2`
(pick = teaser number or title from that day's digest)

## Site repo facts

- Repo: `guideops/guideai_webpage`. Find the checkout: `$GUIDEAI_REPO`, else
  `~/guideai_webpage`, `/root/guideai_webpage`,
  `C:\Users\pawar\ai-workspace\claude-projects\guideai_webpage`. Never guess.
- Deploys to **Cloudflare Pages on merge**. Merging the PR publishes the post;
  there is no separate deploy step.
- Post metadata: `data.js` → `window.SITE_DATA.posts[]`
  `{ slug, title, date, kind: "essay"|"note", readTime, excerpt, tags, cardImage, imageAlt }`
  New posts prepend (array is newest-first).
- **Two insights surfaces**: the homepage section auto-shows the latest 3 from
  `posts[]`; the Insights page (`archive.html`) renders from the curated
  `homepageFeed[]` list. Every new post needs BOTH a `posts[]` entry AND a
  `{ type: "post", slug }` prepended to `homepageFeed[]`, or it is reachable
  only by direct URL.
- Post body: JSX block in `src/post.jsx`, gated
  `{post.slug === "<slug>" && (<article className="prose">…)}`. Structure:
  `<p>`, `<h2>`, `<ul>`, `<blockquote>`. The template renders `cardImage` as
  the article hero automatically.
- Card image: `assets/post-<slug>.webp` (~1200w).
- Build: `npm run build` (babel `src/` → `assets/js/`, which is what is
  served). Commit the compiled output alongside the source.

## Phase 1 — draft (no site edits, no image)

1. **Load context**: read `<vault>/Agentic Output/insights/<date>.md` (resolve
   the vault as in `insights-recon`). Pull the picked teaser's angle and
   sources. Fetch the full source articles (defuddle preferred) so the post
   argues from the actual content, not the digest summary.

2. **Outline first**, blog format: hook, target reader, key promise, then
   sections. Keep it internal unless asked, but write it before prose.

3. **Draft** — opinionated take, Guide's voice:
   - Read 2-3 existing post bodies in `src/post.jsx` for register: direct,
     practitioner-grounded, short paragraphs, concrete examples, a close that
     tells the reader what to do.
   - Essay 800-1500 words (`kind: "essay"`) or note <400 (`kind: "note"`).
   - Cite sources inline as plain links where claims need backing.
   - **Humanizer pass, with these overrides — they beat the site sample:**
     - NO em dashes or en dashes anywhere, including the excerpt. The site's
       older posts have them; the user has ruled them out. Do not match the
       sample on this.
     - NO manufactured punchlines, aphorisms, or mic-drop closers. If a line
       sounds quotable but nobody actually said it, cut it.
     - `<blockquote>` only for a REAL quote from a source, attributed by
       context. Never an invented pull-quote.
     - End on a concrete action or fact, not a kicker.
   - `readTime`: words/220, rounded, "N min". `excerpt`: 1-2 sentences, same
     rules.

4. **Present the draft in chat** (title, excerpt, full body) and STOP. Iterate
   on feedback until the user says it is good. Log voice feedback to
   `domains/content/learnings.md` in the agentic-workspace checkout.

## Phase 2 — image and wiring (only after explicit approval)

5. **Card image** — gpt-image-2 via Codex CLI (ChatGPT subscription, no API key):
   - `codex exec "Generate an editorial blog thumbnail: <art direction>. Save to <repo>/assets/post-<slug>.png"`
   - Art direction from the APPROVED article's core metaphor: editorial,
     abstract-conceptual, site palette (cream field, charcoal, clay `#c15f3c`),
     no text, no logos, no people.
   - Convert to ~1200w webp (`ffmpeg -i in.png -vf scale=1200:-1 out.webp`) and
     delete the png. Raw gpt-image-2 output is ~2.5MB; the webp lands ~40KB.
   - **fal.ai fallback requires explicit user consent first** (key in Bitwarden
     on the VPS). Never fall back silently.
   - Write a real `imageAlt`.

6. **Wire into the site**: `posts[]` entry, `homepageFeed[]` entry,
   `src/post.jsx` block, then `npm run build`. `date` = intended publish date
   (ask if not given; the user schedules 3x/week).

7. **Verify in a browser** before committing: post page (prose + hero image),
   archive card (image loads), zero console errors. Serve with
   `npx http-server -p <port> -c-1` — the `-c-1` matters, default caching
   serves a stale `data.js` for an hour and will fake a passing check.

8. **Branch + commit**: branch `insights/<slug>`, commit only the files this
   post touches (`data.js`, `src/post.jsx`, `assets/js/post.js`, the webp).
   Never sweep in pre-existing working-tree changes. Do NOT push to main or
   merge — open a PR or leave the branch for review. The user sets the final
   date and merges, which deploys.

9. **Log**: append the run to `server/data/runs.json` in agentic-workspace.

## Boundaries

- Phase 2 never starts without the user approving the Phase 1 draft in chat.
- Never merge or deploy. Merging is publishing and that is the user's call.
- Never generate the image via fal.ai without a fresh explicit yes.
- One post per invocation.
