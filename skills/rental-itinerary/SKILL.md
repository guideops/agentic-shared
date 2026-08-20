---
name: rental-itinerary
description: Build a property-viewing itinerary from the operator's 'Apartments' tab in the Sydney rental spreadsheet. Orders viewings High → Medium → Low priority, groups them by location so one trip covers a whole suburb, and costs every hop from the Rydges North Sydney base. Use when the user says /rental-itinerary, "plan the viewings", "viewing plan", "plan of attack", "itinerary for the apartments", or has just updated the Apartments shortlist and wants a fresh route. Rebuild it as often as the list changes.
---

# Rental viewing itinerary

Turns the hand-curated **'Apartments'** tab into a **'Viewing Plan'** tab: what to
see, in what order, on which day, and how long each hop takes.

## Run it

```bash
python3 /opt/agentic/shared/skills/rental-itinerary/scripts/itinerary.py
```

| Flag | Default | Meaning |
|---|---|---|
| `--per-day N` | `4` | Viewings per day. The trip is a fortnight; burning out in three days helps nobody. |
| `--tab NAME` | `Viewing Plan` | Destination tab. Created if missing. |
| `--dry-run` | off | Print the plan, write nothing. |

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
