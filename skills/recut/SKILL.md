---
name: recut
description: Run the recut lead pipeline — find businesses that just started running Meta ads, judge their creative by vision, rebuild it from their own photos, publish a landing page, and draft the outreach message. Use when the user says /recut, "run recut", "check for new leads", "any new advertisers", "rebuild lead N", or asks about the recut project's leads, campaigns, or pipeline state.
---

# recut

Pipeline that finds businesses the week they start advertising, rebuilds their weak ad from their own photos, and hands them the result for free as a way into a monthly content retainer.

Repo: `/root/recut` on the VPS — `C:\Users\pawar\ai-workspace\claude-projects\recut` on the Windows laptop (private, code only — `data/` is gitignored)
Pages: `/root/recut-pages` on the VPS — `C:\Users\pawar\ai-workspace\claude-projects\recut-pages` on the laptop (public, GitHub Pages)
Live at: https://guideops.github.io/recut-pages/

**Always `cd` to the recut repo before running anything. All commands print their own output paths — use them.**

## Lead FSM

`scouted → enriched → judged → built → queued → mailed → scanned → converted`, plus terminal `rejected`.

Every stage is idempotent and re-runnable. The SQLite DB (`data/pipeline.db`) is permanent memory: a Facebook page seen once can never become a lead twice, across any campaign or month. Never suggest a spreadsheet for dedup — the DB already does it.

## Cost rules (state these accurately, never inflate)

Scout, enrich, judge, rebuild, landing page: **$0**. Nothing bills until physical print/postage (~NZ$3.50/card), which only happens on explicit human approval. Vision judging runs inside the Claude Code session, so it costs nothing marginal.

## Modes

### 1. Scan for new leads (`/recut`, "any new leads")

```bash
npm run scout        # scrape active campaigns, detect new advertisers
npm run enrich       # scrape each new lead's own site for contacts + photos
npm run report:html  # data/report.html + data/leads.csv
```

Then judge every lead now sitting at `scouted` (mode 2).

Campaigns live in `config/campaigns.json` — niche + city + query + `active`/`paused`. Switching niche or city is a config edit, never a code change.

### 2. Judge (vision gate — the wallet guard)

For each `scouted` lead, Read its ad screenshot from `data/creatives/<library_id>.png` and score it yourself. Then:

```bash
node src/lead.mjs verdict <id> accept "reason + rebuild angle"
node src/lead.mjs verdict <id> reject "reason"
```

**Reject** when: the ad is already good (branded photos, clear offer, real CTA — they don't need you), the business isn't in the target niche (keyword noise), it's a one-off event with no retainer potential, or it's obviously agency-made.

**Accept** when: generic stock/Canva template, text-soup flyer, no clear offer, or raw unedited phone footage — *and* the business looks real and ongoing.

Rejections are archived, never deleted. Reasons matter — they become the retarget pool.

### 3. Rebuild + publish (per accepted lead)

1. Download 3–4 of their real photos from the `gbp_json` evidence into `data/leads/<id>/photos/` (skip logos, icons, sprites). Read them — verify they're usable job/team photos, not decoration.
2. Write `data/leads/<id>/creative.json`:
   ```json
   {
     "template": "trades-v1",
     "brand": { "name": "...", "color": "#D32F2F", "dark": "#14161a" },
     "photo": "photos/<file>",
     "headline": "Offer-led, not a slogan.",
     "sub": "What + where",
     "bullets": ["concrete", "specific", "three max"],
     "domain": "theirsite.co.nz",
     "cta": "Book a plumber"
   }
   ```
3. `node src/creative.mjs <id>` then **Read the PNG and check it**. Common failures: headline covering faces, CTA text wrapping, bullets sitting on a busy part of the photo.
4. `node src/landing.mjs <id>`, then commit+push in `../recut-pages`. Verify with `curl -s -o /dev/null -w "%{http_code}"` — Pages takes ~40s. Use a background `until` loop to wait, never chained sleeps.
5. Draft `data/leads/<id>/message.txt` (mode 4).

**Templates** (in `src/creative.mjs`):
- `trades-v1` — photo fills frame, text overlaid. For job-site/work photos.
- `team-v1` — text panel on top, photo band below, uncovered. For face-led creatives where the headline must not cover people.

Add a new template when a vertical needs a genuinely different structure; don't fork one for a colour change.

**Copy rules**: offer-led headline over a slogan ("Hot water down? Fixed today." beats "Local. Reliable."), their real suburb, one clear action. Never invent prices, guarantees, certifications, or claims the business hasn't made itself.

### 4. Outreach message

Write `data/leads/<id>/message.txt` — a Facebook page DM. Structure: name the specific ad you saw and when, one honest sentence on why it underperforms, the free rebuild link, then the retainer as an afterthought. Short. No agency voice, no flattery, no "hope this finds you well."

**The user sends it. Never send messages on their behalf.**

### 5. Postcard (physical — only on explicit request)

```bash
node src/postcard.mjs <id>   # needs data/leads/<id>/postcard.json
```
A6 landscape print PDF + 3mm bleed, 2 pages: front is their live ad next to the recut, back is pitch + address block + QR to the landing page. Requires a mailing address in the enrich evidence.

This is the only stage that costs money. Confirm with the user before treating any card as ready to send, and never imply mailing happened.

## Boundaries

- **Never send** a DM, email, or postcard. Draft it, hand it over, stop.
- **Never publish** a rebuilt ad as recut's own marketing without the business's permission — the pages are unlisted gifts for the owner, not portfolio pieces.
- **Take down on first request.** The rebuilds use businesses' own copyrighted photos; that's defensible as a private gift, not as publishing.
- Scout uses logged-out public Ad Library access. Never wire it to a personal Facebook login.
- Don't scale DM volume without flagging that both NZ's Unsolicited Electronic Messages Act and Facebook's own spam limits become real at hundreds per week.

## Reference

`reference.md` in this skill folder holds the full command table, DB schema, JSON spec shapes, and known scraper failure modes. Read it when debugging a stage or extending the schema.
