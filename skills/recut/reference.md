# recut reference

## Commands

| Command | Does | Writes |
|---|---|---|
| `npm run scout` | Scrape Ad Library UI per active campaign, detect new advertisers | `pages`, `ads`, `leads`, `scans` rows; `data/creatives/<library_id>.png` |
| `npm run enrich` | Fetch each `scouted` lead's website + contact page | `leads.gbp_json`, status → `enriched` |
| `npm run report` | Console table of leads + last scans | — |
| `npm run report:html` | Visual report + spreadsheet | `data/report.html`, `data/leads.csv` |
| `node src/lead.mjs list [status]` | List leads | — |
| `node src/lead.mjs show <id>` | Full lead JSON incl. evidence, verdict, ads | — |
| `node src/lead.mjs verdict <id> accept\|reject "notes"` | Judge gate | `leads.verdict_json`, status → `judged`/`rejected` |
| `node src/creative.mjs <id>` | Render ad creative 1080×1350 | `data/leads/<id>/recut/recut-1.png`, status → `built` |
| `node src/landing.mjs <id>` | Generate GitHub Pages landing page | `../recut-pages/for/<slug>/`, `leads.landing_url` |
| `node src/postcard.mjs <id>` | Render A6 print PDF | `data/leads/<id>/postcard.pdf`, status → `queued` |

## DB schema (`data/pipeline.db`, node:sqlite)

- `campaigns` — niche, city, country, query, status. Unique on (niche, city). Synced from `config/campaigns.json` on every scout run.
- `pages` — `page_key` (FB slug or numeric id) PRIMARY KEY, page_name, page_url, first_seen_at, last_seen_at. **This is the dedup memory.**
- `ads` — `library_id` PK, page_key, campaign_id, start_date, n_variants, body_text, creative_img_url, screenshot_path, dest_url, first/last_seen_at.
- `leads` — id, page_key UNIQUE, campaign_id, status, gbp_json, verdict_json, postcard_path, landing_url, mailed_at, notes, timestamps.
- `scans` — per-campaign run log: ads_found, new_ads, new_pages, new_leads, error.

Additive migrations run in `openDb()` via `try { ALTER TABLE } catch {}`. Add new columns there, never by rewriting `schema.sql` alone.

## New-advertiser detection

Constants at the top of `src/scout.mjs`: `MAX_ADS = 3`, `LOOKBACK_DAYS = 14`.

A page becomes a lead when it has ≤ MAX_ADS distinct active ads, its earliest `start_date` is within LOOKBACK_DAYS, and it isn't already a lead. Meta shows only *active* ads outside the EU, so start dates are the only history signal available — this is inference, not ground truth. False positives (a page that paused ads for a year then resumed) are expected and cheap.

## Spec file shapes

`data/leads/<id>/creative.json` — see SKILL.md. `template` must exist in `TEMPLATES` in `src/creative.mjs`.

`data/leads/<id>/postcard.json`:
```json
{
  "business": "Taylor Plumbing",
  "addressLines": ["The Owner", "Business Name", "258 Roscommon Rd", "Wiri, Auckland 2104"],
  "qrUrl": "https://guideops.github.io/recut-pages/for/<slug>/",
  "hook": "Same business. Same budget. <em>Different ad.</em>",
  "pitchLines": ["...", "...", "..."],
  "sender": "recut — ads rebuilt for Auckland trades"
}
```

`data/leads/<id>/message.txt` — plain text FB DM draft.

## Known failure modes

- **"no results marker — possible login wall or layout change"**: scout couldn't find `Library ID:` text within 30s. Debug by launching Chrome non-headless (`HEADFUL=1 npm run scout`) and dumping `document.body.innerText`. Do NOT use Playwright's `waitForFunction` on facebook.com — CSP blocks the injected poll; the code uses a plain `page.evaluate` poll loop instead.
- **Card extraction returns 0**: the DOM walk in `extractCards()` climbs ≤15 parents from each `Library ID: N` leaf looking for a container that also holds `Sponsored`. If Meta restructures, adjust that walk, not the regexes.
- **Screenshot timeout on a card**: caught per-ad; the ad still inserts with `screenshot_path = null`.
- **GitHub Pages 404 after push**: deploy takes ~40s. Wait with a background `until curl … = 200` loop; chained `sleep` calls are blocked by the harness.
- **Enrich returns nothing**: the ad had no outbound link (Send Message CTA). Lead is flagged `[no website in ad]`, not dropped — those often need the most help. Address hunt then requires the NZ Companies Register (api.business.govt.nz, free) or their FB page's About tab.

## Landing pages

`src/landing.mjs` constants: `PAGES_BASE_URL`, `CONTACT_EMAIL` (currently pgtmk101@gmail.com — the page CTA is a `mailto:` with a pre-filled subject). Scan tracking is opt-in and free: sign up at goatcounter.com, set `GOATCOUNTER_CODE`, regenerate pages. GitHub Pages has no server logs, so without it there is no scan data — say so plainly rather than implying tracking exists.

## Fallbacks if the Ad Library scrape breaks

Apify `facebook-ads-library-scraper` (~US$0.75/1k ads) or ScrapeCreators (1000 free credits, 1 request = 1 credit). Both are paid API paths — flag the cost change before switching.
