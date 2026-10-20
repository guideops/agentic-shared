---
name: itinerary-maker
description: Build a travel itinerary for any destination, from either a loose idea or a full brief. Interviews you when details are missing, harvests real activities from Wikivoyage/Wikipedia/OpenStreetMap, adds researched gaps the open data misses, then produces a MENU of mixable day options - each a closed loop from your accommodation - scheduled against real drive times, opening hours and sunset, with a bench of alternates for rain, closures and tiredness. Outputs a workbook and a phone-readable PDF. Use when the user says /itinerary-maker, "plan a trip", "itinerary for X", "what should I do in X for N days", or names a destination and some dates.
---

# Itinerary maker

Produces **options, not a verdict**. The traveller decides, curates and polishes;
this gives them a well-researched menu with the arithmetic already done.

Every day option is a **closed loop from the accommodation**, which is what makes
them mixable: take Day 1 from one option and Day 2 from another and the geography
still holds. Each scheduled stop carries a **bench** - two or three alternates
tagged with why you would swap (rain, closed, running late, cheaper) - because
weather happens and nobody wants a plan with no back pocket.

## Run it

```bash
cd /opt/agentic/shared/skills/itinerary-maker
python3 scripts/harvest.py --dest "Queenstown" --region "New Zealand" \
        --trip queenstown-aug --day-trips "Milford Sound,Glenorchy,Arrowtown,Wanaka"
# write trips/<slug>/brief.json      (see below)
# write trips/<slug>/overrides.json  (your research - see below)
python3 scripts/plan.py  --trip queenstown-aug
python3 scripts/xlsx.py  --trip queenstown-aug
python3 scripts/pdf.py   --trip queenstown-aug
```

| Script | Does | Key flags |
|---|---|---|
| `harvest.py` | gathers and structures candidates | `--day-trips`, `--auto-day-trips N`, `--districts N`, `--radius-km`, `--max-drive-mins`, `--no-overpass`, `--images N` |
| `plan.py` | scores, builds day options, schedules the clock | `--dry-run`, `--options-per-day` |
| `xlsx.py` | 5-sheet workbook | `--out` |
| `pdf.py` | A5 phone PDF | `--out`, `--no-photos` |

Outputs default to `/root/Documents/Hermes/<slug>-itinerary.{xlsx,pdf}`.

## Step 0: the interview

If the user gave a loose idea ("3 days in Lisbon"), ask before building. Use the
`/align` format - numbered questions, lettered options, plain text, one turn,
then build. **Never ask what they already told you.** The nine slots:

1. Destination and region  2. Dates and number of days  3. Where they are staying
4. How they are getting around (car / walking / public / bike)  5. Pace
(relaxed / moderate / packed)  6. Interests  7. Anything already booked
8. Party (adults, kids)  9. Output format - **ask this, do not assume**

Interests map to these theme keys: `adrenaline scenic walking food wine culture
snow relax family`.

**Ask about the party whenever it is more than two people.** Who is coming
decides almost everything downstream, and it is cheap to ask and expensive to
assume:

- **"Who is coming, and does everyone do everything?"** The single most
  load-bearing question. A group of seven is rarely one itinerary.
- **"Who is driving?"** Name a primary and a backup per vehicle. Everyone who
  might drive has to be on the rental agreement at the desk; adding a driver
  afterwards is a phone call and a fee.
- **"Is anyone opting out of the headline activity?"** Skiing, diving, a long
  hike - whatever the trip is nominally about. If yes, the opt-outs need their
  own track, not a note.
- **"Is anyone paired up?"** Partners want a day together, and it changes both
  the schedule and the de-duplication.
- **"Anything undecided?"** Record it as undecided rather than guessing.
  `"skis": "undecided"` is flagged in the workbook; a guess is not.

Record the answers as `people`, which is the base every other sheet keys off:

```json
"people": [
  {"key": "pawarid", "name": "Pawarid Tupmongkol", "short": "Pawarid", "seat": "25A",
   "is_you": true, "roles": ["organiser", "driver", "skier"],
   "drives": "primary", "skis": true},
  {"key": "pracha", "name": "Pracha Tupmongkol", "short": "Pracha",
   "roles": ["backup driver"], "drives": "secondary", "skis": "undecided"}
]
```

`drives` is `primary` / `secondary` / `no`. `skis` is `true` / `false` /
`"undecided"` - anything not boolean is highlighted in the workbook, because an
undecided lift pass is a price that has not been settled.

Track `members` then reference these keys, and `--split` produces one PDF per
person, each with their own name, seat, roles, days, packing list, cost, and
**only their own boarding pass**.

Then write `trips/<slug>/brief.json`:

```json
{ "destination": "Queenstown", "region": "New Zealand",
  "start_date": "2026-08-28", "days": 3, "utc_offset_hours": 12,
  "base": {"name": "...", "lat": -45.03, "lon": 168.66},
  "transport": "car", "pace": "moderate",
  "interests": ["scenic", "snow", "wine"], "party": {"adults": 2}, "fixed": [] }
```

`utc_offset_hours` matters - sunset is computed, and longitude alone does not
give you a timezone. `timezone` (an IANA name) is used for the forecast.

### Fixed anchors and day windows

Anything already nailed down goes in `fixed`, and is placed at its stated time
with the flexible stops fitted around it. This is the only honest way to
schedule a travel day: the plane lands when it lands.

```json
"day_windows": { "2026-08-24": ["10:30", null], "2026-08-26": [null, "15:45"] },
"fixed": [
  {"date": "2026-08-24", "start": "10:30", "end": "11:15",
   "name": "Land, collect the rental car", "lat": -45.019, "lon": 168.743,
   "note": "Allow the full 45 min - bags plus the rental desk."},
  {"date": "2026-08-26", "start": "15:45", "end": "17:30", "terminal": true,
   "name": "Return the car, fly out"}
]
```

`terminal: true` on the last anchor stops the day routing back to base - you
end at the airport, not at the accommodation. A fixed item can supply
`geocode_as` instead of coordinates.

Two rules the scheduler enforces around anchors, both learned the hard way:

- **A fixed anchor de-duplicates the flexible pool**, matched loosely. The
  anchor "Skyline Gondola + Luge" covers the candidates "Skyline Gondola" AND
  "Luge"; exact matching caught neither and the plan sent the traveller up the
  same hill on two days.
- **Options are paired to dates, not chosen and dated afterwards.** Weather, the
  day's window and the flight home are properties of the DATE. Choosing first
  put bungy jumping on a 95%-rain day and a Wanaka day trip on a departure
  morning with snow forecast.

## Step 2: research the gaps, in `overrides.json`

**This step is not optional and the scripts cannot do it.** Open data is good at
*where things are* and bad at *what is worth doing this month for this price*.
Harvest Queenstown and you get 63 curated listings and still no Milford Sound
cruise, no Gibbston wine, and bungy prices from 2017.

So: web-search the destination for the traveller's actual dates, then write
`trips/<slug>/overrides.json`. `patch` corrects a harvested entry by name; `add`
introduces something the sources missed. Anything here wins.

```json
{ "patch": [ {"name": "Luge", "price": "$99 adult (2026)", "hours": "Daily from 10:00"} ],
  "add":   [ {"name": "Milford Sound nature cruise", "geocode_as": "Milford Sound, New Zealand",
              "kind": "do", "duration_min": 120, "price": "NZ$85-120",
              "themes_hint": "scenic", "indoor": false, "desc": "..."} ] }
```

Search at minimum: **what is open in that month**, **current prices for the
marquee items**, **seasonal events**, and **whether the marquee day trip is
better guided than self-driven**. Record your sources in the file.

`geocode_as` is geocoded verbatim - do not repeat the region if it is already in
the string. `themes_hint` beats keyword guessing. A patch carrying `price` or
`hours` clears that entry's stale flag automatically.

Also supported in `overrides.json`:

- `"exclude": ["The Remarkables Ski Area", ...]` - drops candidates by name.
  **Applied after the additions**, because an earlier version excluded first and
  an override that re-added a name defeated the exclusion silently.
- `"only_weekdays": ["wed", "fri"]` on an entry - for things that do not run
  every day. Coronet Peak's night ski sat in a Tuesday pool unfiltered and
  helped push the actual ski day off the end of the clock.
- `"price_nzd": [230, 290]` - an explicit range that bypasses price parsing.

### Groups and tracks

A party does not always stay together. Declare the groups, then give each date
one or more tracks; each track is planned as its own day.

```json
"groups": {
  "skiers": {"label": "Skiers (you + 3)", "size": 4},
  "non-skiers": {"label": "Non-skiers (your partner + 2)", "size": 3}
},
"tracks": {
  "2026-08-25": [
    {"group": "skiers", "primary": true, "prefer": "local-snow", "lineages": ["you"]},
    {"group": "non-skiers", "prefer": "relax", "lineages": ["partner"],
     "window": ["08:30", "17:30"], "note": "back before the evening"}
  ]
}
```

- `primary` marks the track **you** are on. The trip cost total follows it -
  summing every track would bill one person for two groups being in two places
  at once. `cost_by_group` reports each group separately.
- `lineages` is a **list of people**, not a group name, and is what
  de-duplication runs on. The Wednesday couple's day must avoid what BOTH of
  them already did, and they spent Tuesday apart.
- `window` gives a track its own hard start and finish - the non-skiers hand
  your partner back at 17:30 for an evening promised to her.
- A fixed anchor may name a `track`; without one it belongs to everyone that
  day. Day capacity is computed per track, or the skiers get charged for the
  non-skiers' spa booking.

### Pinning a day

`"day_preferences": {"2026-08-25": "local-snow"}` in the brief nails an option
to a date. A preference beats fit, because the traveller knows things the
scorer does not.

## Weather

`plan.py` pulls a daily forecast for the base coordinates and the trip dates
(Open-Meteo, free, keyless, cached). Inside the ~16-day horizon it is a real
forecast; beyond that it returns nothing and says so, because a made-up
forecast invites packing decisions with nothing behind them.

**The day is judged on the hours you are actually out (08:00-18:00), not on a
24-hour total.** This is the single most important thing about the weather
layer. A day with 10 mm that all falls overnight is a dry day for every purpose
that matters - and judging it on the daily sum marked a dry, calm ski day as
"95% rain, keep indoor options ready" and moved the skiing to a day with 25 mm
of rain on it. The 24-hour figure is kept for context and reported separately.

For anything at altitude, check the forecast at the ELEVATION, not in the
valley. Pass `elevation` to Open-Meteo and read `freezing_level_height`: if the
freezing level sits above the summit, precipitation falls as rain on the
snowpack even when the valley forecast says snow.

The forecast is not decoration - it changes the plan:

- Wet or snowy days sort indoor stops to the front.
- A snow day with 20 mm-plus of rain drops exposed outdoor stops outright.
- `day_fit` penalises outdoor-heavy options on bad days and rewards them on
  good ones, so the good weather gets spent outdoors.
- Long mountain day trips are heavily penalised on snow days.

## Never swallow an exception around per-person work

`build_html` had `except Exception: pass` around the per-person packing
rebuild. A local variable named `packing` shadowed the imported module for the
whole function, the rebuild raised `UnboundLocalError` on every call, and every
personal copy silently shipped the whole party's gear list - a non-skier told
to pack goggles. It looked right because a plausible list was still printed.

Print the failure. A visible miss is worth more than a silent fallback that
reads as correct.

## Per-person editions

`pdf.py --split` writes one PDF per **person**, plus the combined one. A
non-skier should not be carrying eleven pages about a ski day.

Membership is declared on each track:

```json
{"group": "skiers", "members": ["you", "friends"]}
```

`members` is deliberately separate from `lineages`. Lineages drive
de-duplication; members drive who carries which copy. Filtering by track NAME
instead dropped the arrival day from the skiers' edition, because on the
arrival day their track is called "everyone".

Each edition rebuilds its own packing list and its own cost total from that
person's days only. `packing.build()` therefore reads the anchors off the
scheduled **timelines**, never off `brief["fixed"]` - the brief lists every
track's commitments, so building from it told a non-skier to pack goggles for
a lift pass that was never on her day.

`--group <name>` renders a single edition.

## Tickets and passes

`ticket_rules` in the brief decides who carries what, by ROLE not by name:
`{"match": "car-", "audience": "drivers"}` puts the rental agreements only in
the copies of people whose `drives` is primary or secondary;
`"audience": "organisers"` keys off the `organiser` role; `"everyone"` is for
genuinely shared logistics like a shuttle map. Anything unmatched is personal
and goes only to the person whose key the filename contains.

`ticket_notes` pins a short operational panel under the ticket it belongs to -
`{"match": "shuttle", "title": ..., "blocks": [{"heading": ..., "lines": [...]}]}`.
Rental terms run to pages; what somebody needs standing in an arrivals hall is
the phone number, the door, and the two things that cost money if they get them
wrong. Summarise to that and put it where they will be looking.

A `.pdf` cannot be embedded as an image - rasterise it first
(`pdftoppm -png -r 130`) and drop the resulting page images into `tickets/`.


Drop screenshots - boarding passes, Apple Wallet grabs, booking confirmations -
into `trips/<slug>/tickets/` as `.png`/`.jpg`. **Name each file after the
person it belongs to** (`2-ji-yeon-25B.jpeg`): a personal edition matches the
filename against that person's key - punctuation stripped from both sides -
and carries only their pass. Handing everyone a PDF containing all seven
boarding passes and their QR codes is not a courtesy. They are embedded as data URIs
(so they work with no signal), collected onto a **Tickets & passes** page, and
page one grows a button in its top-right corner that jumps straight there.
No tickets, no button.

## The PDF

Page one is a **tappable contents page**: every date, its forecast, and a card
per group showing who they are, what they are doing, when, and what it costs.
Each card links to that group's page - Chrome keeps internal anchors when it
prints, so the links work in any PDF reader.

Page one also carries a **Packing list** card showing just the essentials, with
a link to the full list at the back.

**Meal slots name no restaurant when nothing is booked.** The card points at
the Food & drink page instead, and outside the base town it names the one place
worth knowing about in that area ("Arrowtown highlight: Wolf Coffee"). A plan
that prints a restaurant name reads as a reservation; it is not one.

**Every link must be verified before it ships.** Curl each one and check for a
200 - a dead link in a document somebody is holding in a car park is worse than
no link. Sites that 403 a scripted request (Millbrook, newzealand.com) may
still be fine in a browser, but do not ship them without saying so.

Set `"area"` on each dining entry, and `"highlight_only": true` outside the
base town so those areas show one entry rather than a full list.

**Curated `ideas` replace the auto-generated options page** once the traveller
knows what they want. Each is `{name, why, cost, links: [[title, url], ...]}` in
the brief and renders as "Other things you could do".

Meal slots offer the nearest few places from the traveller's own list, not
one auto-assigned restaurant.** Each carries its price, distance, a map link
and a menu link - saved-places behaviour, because nothing is booked yet, plans
move during the day, and three you can choose between beats one picked for you.
Set `"dining_only_mine": true` in the brief once the traveller has supplied a
shortlist: where to eat is taste, and a gazetteer has no opinion worth
overriding theirs with.

Give a venue `"maps_query": "Roki Queenstown"` when it is not in OpenStreetMap.
Newer restaurants often are not, and a search by name beats a pin on an
approximate coordinate. `"meal": "breakfast" | "lunch" | "dinner" | "drinks"`
stops a coffee roastery being served as dinner, and a bar can never fill a meal
slot at all.

Food is not a footnote. Meals render as their own cards with the venue, price
and a booking link, and there is a **Where to eat** page listing every option
with the traveller's own picks flagged first.

## Prices

Every priced item is parsed into a per-adult range, converted to the local
currency and totalled per day and per trip. Both outputs carry it: the workbook
gains a "Price as quoted" and an "Est. NZ$ pp" column with day subtotals, the
PDF puts a chip on each card and a total on the cover.

Three rules earn their place:

- **A number only counts as money when a currency symbol is attached.** Without
  that anchor "6 luge rides" became $6 and "13 Jun to 4 Oct 2026" became a
  $4-$2026 range.
- **"Free" and "no price found" are different claims.** Printing the first for
  the second is a lie the traveller discovers at the counter, so a day with
  nothing priced says so and reports its unpriced count.
- **`price_nzd: [low, high]` in an override beats parsing.** Some prices are
  additive - a lift pass PLUS rental PLUS outerwear - and reading min/max out
  of that sentence understates the day badly.

Exchange rates live in `lib/money.py` (`RATES` / `RATES_AS_OF`) and are stated
in the output rather than hidden, because they age.

## Packing list

Generated into `plan.json` and rendered as a workbook sheet and a PDF page.
Every line traces to a real cause - a temperature in the forecast, a stop on
the itinerary, a commitment in the brief - so it reads as "34 mm forecast on
the wettest day" rather than "it might rain".

Gear implied only by a **bench** option is softened to optional and labelled,
because packing ski trousers for a day you are not skiing has a real cost.
Activity matching reads stop NAMES only, never descriptions: the Luge blurb
warns it "closes in high wind or heavy snow", which an earlier version read as
a ski day.

## How the plan is decided

1. **Score** - substance, photo, provenance, interest match. Penalties for
   generic categories ("Cycling"), map labels ("above paragliding spot"),
   everyday amenities (libraries, supermarkets), seasonal-closure hints, and
   distance. Research entries get a deliberate bonus.
2. **Cluster** - candidates group by day-trip hub, or into themed local loops.
3. **Order** - exhaustive best order up to 6 stops, nearest-neighbour beyond.
4. **Schedule** - real drive times, opening hours, meal slots, sunset. A stop is
   dropped if it closes before you arrive, would run past dark while outdoors,
   needs more than a 75-minute wait, or leaves no time to get home.
5. **Recommend** - highest scoring, but varied, and **de-duplicated across days**,
   with a fatigue rule so two long days never sit back to back.

Two safety rules are hard-coded: **no cellar door before a lift pass** (or a
bungy, jet boat or skydive) on the same day, and outdoor stops are never
scheduled to end after dark.

Restaurants are never scheduled as sights. They are held back and dropped into
the meal slots of whichever day you pick.

Days are also constrained by **how far they may spread**, which depends on how
you are getting around: 2.5 km on foot, 9 km by bike, 45 km by car. Without it a
walking day happily strung four excellent museums across Lisbon with 86-minute
legs between them - every stop good, the day unusable.

If de-duplication hollows a day out below four hours, an unused option is
scheduled in its place instead. The real length of a day is only knowable after
re-scheduling, so that swap happens there, not at selection time.

## Read this before trusting a number

- **Prices and hours are open data of varying age.** The `Data age` column gives
  each entry's age; anything marked VERIFY is folklore until checked. A 2017
  Wikivoyage price is nine years stale and reliably low.
- **Drive times are real routes** over the road network via Valhalla, except a
  leg marked `est`, which means the router was unreachable and it fell back to a
  calibrated straight-line estimate.
- **Sunrise/sunset are computed** for the exact date and latitude. Outdoor stops
  are never scheduled to end after dark.
- **Overpass names things like a surveyor.** It is used for coordinates and gap
  filling only, never as the answer to "what is worth doing".
- **The base changes every number.** If `brief.json` says `"assumed": true`,
  every drive time in both outputs is provisional.

## Gotchas paid for already

- **Wikimedia rate-limits hard.** Both APIs are throttled with backoff. Do not
  remove it; sixty unthrottled calls earns a 429 mid-harvest.
- **The big activity marketplaces block this server** - GetYourGuide, Viator,
  Klook, TripAdvisor and newzealand.com all return 403 to both curl and
  WebFetch. Do not build on them. These DO answer, and carry named tours with
  prices, so use them for the research step:
  - the destination's **official tourism site** (e.g. `queenstownnz.co.nz`) -
    the best source of the four, and the one that flags seasonal and
    wet-weather options
  - `civitatis.com` (prices in USD), `musement.com`, `headout.com`
  Plus web *search*, which surfaces marketplace content without the 403.
- **A base town's own listings stop at its outskirts.** Always pass
  `--day-trips` or `--auto-day-trips`, or you get a Queenstown plan with no
  Milford Sound in it.
- **Big cities keep their listings on district subpages.** Lisbon's main article
  is mostly transport and tourist-office practicalities; the actual sights live
  on `Lisbon/Alfama`, `Lisbon/Belém` and four more. `--districts` (default 8)
  harvests them. Without it, Lisbon's top-scoring "attractions" were a fashion
  week and a tourist information desk, with no Jerónimos and no Belém anywhere.
  Small towns like Queenstown have no subpages and are unaffected.
- **Wikimedia serves pre-rendered thumbnail sizes only**, and which sizes exist
  differs per image. Do not rewrite an image URL to a fixed width - a blanket
  rewrite to `1024px-` earned a 400 on nearly every photo. Take the size the API
  hands you and fall back through `_variants()` in `pdf.py`.
- **Never key a disk cache on `hash()`.** Python randomises string hashing per
  process, so the photo cache never hit and re-downloaded on every run.
- **Negative geocodes are cached and versioned.** If you change how queries are
  built, bump `NEGATIVE_VERSION` in `lib/geo.py` so old misses get retried.
- Nominatim can land on a linear feature rather than a visitor entrance - a
  routed distance far above the straight-line distance is the tell.

## Files

```
lib/geo.py        geocoding, routing, caches, Overpass
lib/sun.py        sunrise/sunset (NOAA, no network)
lib/weather.py    daily forecast (Open-Meteo, free/keyless, ~16-day horizon)
lib/packing.py    packing list derived from the forecast and the actual plan
lib/money.py      price parsing, NZD conversion, day and trip cost roll-up
scripts/          harvest.py  plan.py  xlsx.py  pdf.py
cache/            geocode.json, routes.json, tiles/, photos/   (shared across trips)
trips/<slug>/     brief.json, overrides.json, candidates.json, plan.json
```

`plan.json` is self-contained: `pdf.py` runs from it on any machine, no
credentials needed. Caches are shared, so a second trip to the same region is
close to free.
