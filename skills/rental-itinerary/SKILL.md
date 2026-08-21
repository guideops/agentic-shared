---
name: rental-itinerary
description: Build a property-viewing itinerary from the operator's 'Apartments' tab in the Sydney rental spreadsheet. Orders viewings High → Medium → Low priority, groups them by location so one trip covers a whole suburb, and costs every hop from the Rydges North Sydney base, then renders both a 'Viewing Plan' sheet and a phone-readable PDF with per-day maps and tappable links. Use when the user says /rental-itinerary, "plan the viewings", "viewing plan", "plan of attack", "itinerary for the apartments", or has just updated the Apartments shortlist and wants a fresh route. Rebuild it as often as the list changes.
---

# Rental viewing itinerary

Turns the hand-curated **'Apartments'** tab into a **'Viewing Plan'** tab and an
illustrated **PDF**: what to see, in what order, on which day, and how long each
hop takes. The sheet is where you check and correct the data; the PDF is what
you carry on your phone.

## Run it

```bash
python3 /opt/agentic/shared/skills/rental-itinerary/scripts/itinerary.py
```

| Flag | Default | Meaning |
|---|---|---|
| `--per-day N` | `4` | Viewings per day. The trip is a fortnight; burning out in three days helps nobody. |
| `--tab NAME` | `Viewing Plan` | Destination tab. Created if missing. |
| `--dry-run` | off | Print the plan, write nothing. |
| `--pdf [PATH]` | off | Also render the illustrated PDF. Default path `/root/Documents/Hermes/viewing-itinerary.pdf`. |
| `--fetch-photos` | off | Download listing photos into `photos/`. **Laptop only** - see below. |

## The PDF

```bash
python3 .../itinerary.py --pdf              # plan + sheet + pdf
python3 .../scripts/pdf.py                  # re-render from the last plan.json
```

A5 portrait, built for reading on a phone while you are moving. One card per
viewing: number, priority, `$/wk`, the travel leg from the previous stop, the
station and its walk verdict, your own comments, and two **tappable** links -
`Open listing` and `Directions` (a Google Maps deep link to the exact
coordinates).

Each day opens with **two** maps, because they answer different questions:

1. **`B` &rarr; `1`** - the hotel to the first viewing, framed to fit both, with
   the rail leg dashed and the route and minutes in the header.
2. **The detail map** - that day's stops at street level, solid line in visiting
   order. The dashed leg runs off the edge toward the hotel, so you can see
   which way you came in.

One map cannot do both: a frame wide enough to hold the hotel shrinks the day's
actual stops to specks. Properties that share a suburb centroid are fanned out
so every number stays readable.

Everything in the PDF is derived from the sheet. Correct data on **Apartments**,
never in the PDF.

### Costs nothing

Map tiles come from `tile.openstreetmap.org` (free, no key, cached in
`tile-cache/`). Rendering is local headless Chrome. **No Apify call is made by
this skill at any point** - Apify is only ever touched by the daily watcher cron.

### Photos need your laptop

Domain's image CDN refuses this server (Kuala Lumpur; every request 400s), the
same wall that forces `rental-search` onto a residential connection. The photo
*URLs* are free - they arrive inside the Apify payload the cron already pays for
and are stored in `state.json`. Only the bytes are blocked.

So: run `--fetch-photos` from your laptop. Photos land in
`photos/<listing_id>.jpg` and every later render, server-side included, picks
them up from that cache. A stop with no cached photo still renders - it just
shows the map pin instead of an empty frame.

**A residential IP is necessary but not sufficient.** Both the listing pages and
the image CDN refuse a plain `urllib` GET outright - 403 from domain.com.au, 429
from realestate.com.au, 400 from the image CDN - because the tell is the client,
not only the address. So this reuses **`rental-search`'s `browser.Session`**: a
real Chromium under patchright, sharing that skill's cookie profile, with the
image bytes pulled through the browser context's own request API so the signed
CDN urls are served to the client that loaded the page. There is deliberately no
urllib fallback; it would only add a guaranteed failure to every run.

That makes `rental-search` a hard prerequisite for photos:

```bash
pip install patchright && patchright install chromium
```

Without it you get a warning and an itinerary with no photos - never a crash.

Two sources, tried in order: the stored Apify urls, then the listing page's
`og:image` tag. The second is what covers hand-added rows that never went
through the watcher and so have no stored urls at all.

### Rendering the PDF away from the server

`plan.json` is committed on purpose. It carries everything the renderer needs -
coordinates, listing ids, comments and photo urls - so on a laptop this is the
whole job:

```bash
git pull
python3 skills/rental-itinerary/scripts/pdf.py --fetch-photos
```

No service-account key, no `state.json`, no copy of the watcher. `plan.json` is
refreshed on the server every time `itinerary.py` runs, so pull before you
render. Needs `Pillow` and Chrome; without Pillow you get the cards and no maps.

Takes 1–3 minutes: it geocodes any new addresses and routes real walking paths.
Both are cached, so a re-run after adding two properties only costs those two.

## How it decides

1. **Priority picks the area.** All High-priority clusters come before any
   Medium-only cluster, and so on. Priority is read from the `Priority` column;
   `Middle`, `med`, `mid` and any casing all normalise to the three real tiers.
2. **Geography fills the day.** Properties within 2.5 km chain into one cluster.
   Once a trip is going to a suburb for a Medium, the Lows in that same suburb
   get picked up on the same day rather than earning their own trip across the
   city. Those rows say `already in the area` in `why_now`.
3. **Within a day, priority still leads** — you see the one you care about while
   you still have energy, not after four others.
4. **A hop over 25 minutes starts a new day.** Crossing the city mid-afternoon
   is exactly how a viewing trip goes wrong.
5. **Every leg is costed** from Rydges North Sydney: walking under 1.2 km,
   otherwise walk → rail → walk, with an interchange penalty when the lines differ.

## No clock times, on purpose

Agents set inspection times; you cannot. This gives you the **order** and the
**hop durations** so you can drop real times in as they get booked, and see
immediately whether a proposed slot is reachable from the previous one.

## Columns it writes

`day`, `stop`, `priority`, `why_now`, `suburb`, `address`, `cost_pw`, `from`,
`travel_via`, `travel_mins`, `station`, `walk_from_station_mins`, `walk_rule`,
`located_by`, `your_comments`, `link`

The PDF additionally uses `plan.json`, a sidecar written next to the skill
holding each stop's coordinates and listing id - the things a flat sheet has no
column for.

`walk_rule` scores each property against the operator's station rule — under
8 min preferred, up to 10 tolerated, over 10 is out. `your_comments` carries
their own notes through so the plan is usable without flipping tabs.

## Read this before trusting a number

- **`located_by: SUBURB ONLY`** means the link carried no street address —
  realestate.com.au URLs never do. Those rows are pinned to the suburb centroid,
  so their walk time and travel legs are estimates. Adding the property's
  **Domain** link to the Apartments tab fixes it exactly.
- **Rail times are modelled**, not looked up: 35 km/h average plus a 6-minute
  interchange penalty. There is no free keyless transit router for Sydney.
  Good enough to sequence a day, not a substitute for the Opal trip planner.
- **The tab is fully rewritten each run.** Notes typed onto 'Viewing Plan' will
  be lost — put them on 'Apartments', which this skill only ever reads.

## Safety

Writes to **'Viewing Plan'** only. `sheets.replace` refuses any tab whose row 1
is not this table's header, so 'Basic Costs' and 'Apartments' cannot be hit even
if a gid is wrong. This guard exists because an unguarded write once destroyed a
row of the operator's moving-cost list.
