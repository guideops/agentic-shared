#!/usr/bin/env python3
"""A packing list derived from the plan, not from a template.

Every line traces to something real: a temperature in the forecast, an activity
on the itinerary, or a commitment in the brief. That is the whole point - a
generic "winter trip" list tells you to bring a coat, while this one tells you
to bring chains-capable footwear because there is snow forecast on the morning
you drive to the airport.
"""
from __future__ import annotations

ESSENTIAL, RECOMMENDED, OPTIONAL = "essential", "recommended", "optional"

# Activity keywords -> what they oblige you to carry.
ACTIVITY_GEAR = [
    (r"ski|snowboard|snow|coronet|remarkables|treble cone",
     [("Ski jacket and trousers", ESSENTIAL, "you have a ski day scheduled"),
      ("Goggles", ESSENTIAL, "ski day - sunglasses are not enough in flat light"),
      ("Thermal base layers", ESSENTIAL, "ski day"),
      ("High-factor sunscreen", ESSENTIAL, "snow reflects UV; August sun still burns"),
      ("Waterproof gloves", ESSENTIAL, "ski day"),
      ("Ski socks", RECOMMENDED, "ski day - one pair per day on the mountain")]),
    (r"luge|gondola",
     [("Warm gloves", ESSENTIAL, "the luge track is open-air and unheated"),
      ("Beanie", RECOMMENDED, "gondola and luge in August")]),
    (r"hot pool|onsen|spa|thermal",
     [("Swimwear", ESSENTIAL, "hot pools are on the plan or the bench"),
      ("Flip-flops", OPTIONAL, "hot pools")]),
    (r"hike|walk|track|trail|kepler|tramp",
     [("Waterproof walking shoes or boots", ESSENTIAL, "there is walking on the plan"),
      ("Daypack", RECOMMENDED, "for the walking legs")]),
    (r"bungy|jet ?boat|raft|skydiv|canyon|quad|zipline",
     [("Contact lenses rather than glasses", RECOMMENDED,
       "glasses do not survive a bungy or a jet boat"),
      ("A change of clothes in the car", RECOMMENDED, "jet boat and rafting get you wet")]),
    (r"cruise|milford|fjord|sound",
     [("Seasickness tablets", OPTIONAL, "there is a cruise on the plan"),
      ("Waterproof phone pouch", RECOMMENDED, "spray on deck")]),
    (r"wine|cellar|winery|brewery|distiller",
     [("A way to carry bottles home", OPTIONAL, "wine tasting is on the plan"),
      ("Agree your driver before you go", ESSENTIAL,
       "cellar-door tastings and a rental car do not mix")]),
    (r"gallery|museum|arts centre",
     [("Something to read or do between openings", OPTIONAL,
       "galleries keep short hours - there will be gaps")]),
]


def _matches(pattern, blob):
    import re
    return bool(re.search(pattern, blob, re.I))


def build(plan: dict) -> list[dict]:
    """Returns grouped sections: [{'section': ..., 'items': [...]}].

    A trip can prune the result: `packing_exclude` drops individual items by a
    case-insensitive substring, `packing_exclude_sections` drops whole sections.
    Travellers know what they already carry, and a list padded with things they
    ignore is a list they stop reading.
    """
    import re

    brief = plan.get("brief", {})
    forecast = plan.get("forecast", {}) or {}
    days = plan.get("plan", [])

    # Everything the trip actually contains, as one searchable blob.
    # Scheduled and bench are tracked apart on purpose. Gear for something you
    # are actually doing is essential; gear for something merely on the bench is
    # a maybe, and packing ski trousers for a day you are not skiing has a real
    # cost in a carry-on.
    blob_parts, bench_parts = [], []
    has_outdoor, has_fixed_car, has_flight = False, False, False
    for d in days:
        for it in d.get("timeline", []):
            # Names only. Descriptions mention other activities in passing -
            # the Luge blurb warns it "closes in high wind or heavy snow", which
            # an earlier version read as a ski day and told you to pack goggles.
            blob_parts.append(it.get("name", ""))
            if it.get("type") == "stop" and not it.get("indoor"):
                has_outdoor = True
            for b in it.get("bench", []) or []:
                bench_parts.append(b.get("name", ""))
    # Read the anchors off the scheduled timelines, NOT off brief["fixed"].
    # The brief lists every track's commitments, so a per-person copy built
    # from it told a non-skier to pack goggles for a lift pass that was never
    # on her day.
    for d in days:
        for it in d.get("timeline", []):
            if it.get("type") != "fixed":
                continue
            name = it.get("name", "")
            if re.search(r"rental|hire car|collect the (rental )?car", name, re.I):
                has_fixed_car = True
            if re.search(r"fly|flight|depart|airport|land", name, re.I):
                has_flight = True
    blob = " | ".join(blob_parts)
    bench_blob = " | ".join(bench_parts)

    sections = []

    # ---------------- weather ----------------
    wx_items, seen = [], set()

    # Dedupe on the thing itself, not the phrasing. "Warm gloves", "Waterproof
    # gloves" and "Beanie and gloves" are one pair of gloves in a bag, and a
    # list that asks for all three reads as though nobody checked it.
    CANON = ["gloves", "beanie", "sunscreen", "goggles", "thermal", "walking shoes",
             "waterproof jacket", "over-trousers", "swimwear", "daypack",
             "power bank", "adaptor", "socks"]

    def canon_key(name):
        low = name.lower()
        for c in CANON:
            if c in low:
                return c
        return low

    def add(items, target):
        for name, prio, why in items:
            k = canon_key(name)
            if k in seen:
                continue
            seen.add(k)
            target.append({"item": name, "priority": prio, "why": why})

    if forecast:
        tmin = min(v["temp_min"] for v in forecast.values())
        tmax = max(v["temp_max"] for v in forecast.values())
        feels = min((v.get("feels_like_min") if v.get("feels_like_min") is not None
                     else v["temp_min"]) for v in forecast.values())
        rain_total = sum(v["rain_mm"] for v in forecast.values())
        rain_worst = max(v["rain_mm"] for v in forecast.values())
        snow_total = sum(v["snow_cm"] for v in forecast.values())
        gust = max((v.get("gust_kmh") or 0) for v in forecast.values())
        wet_days = [d for d, v in forecast.items() if v["band"] in ("wet", "snow")]

        if rain_worst >= 5 or rain_total >= 10:
            add([("Waterproof jacket with a hood", ESSENTIAL,
                  f"{rain_worst:.0f} mm forecast on the wettest day, "
                  f"{rain_total:.0f} mm across the trip")], wx_items)
        if rain_worst >= 20:
            add([("Waterproof over-trousers", RECOMMENDED,
                  f"{rain_worst:.0f} mm in one day is not drizzle"),
                 ("A second pair of shoes", ESSENTIAL,
                  "wet shoes do not dry overnight in a 3-day trip"),
                 ("Dry bag or a few plastic bags", RECOMMENDED,
                  "for wet layers in the car")], wx_items)
        if snow_total > 0.05:
            add([("Footwear with grip for snow and slush", ESSENTIAL,
                  f"{snow_total:.1f} cm of snow forecast"),
                 ("Waterproof gloves", ESSENTIAL, "snow forecast")], wx_items)
        if feels <= 0:
            add([("Thermal base layer", ESSENTIAL, f"feels like {feels:.0f}°C at its coldest"),
                 ("Beanie or warm hat", ESSENTIAL, f"feels like {feels:.0f}°C"),
                 ("Warm gloves", ESSENTIAL, f"feels like {feels:.0f}°C"),
                 ("Thick socks", RECOMMENDED, "cold mornings")], wx_items)
        elif tmin <= 6:
            add([("Warm mid-layer - fleece or down", ESSENTIAL,
                  f"mornings down to {tmin:.0f}°C"),
                 ("Beanie", RECOMMENDED, f"mornings down to {tmin:.0f}°C"),
                 ("Warm gloves", RECOMMENDED, f"mornings down to {tmin:.0f}°C"),
                 ("Scarf or buff", OPTIONAL, "wind off the lake")], wx_items)
        if tmax - tmin >= 6:
            add([("Layers rather than one heavy coat", RECOMMENDED,
                  f"the day swings from {tmin:.0f}°C to {tmax:.0f}°C")], wx_items)
        if gust >= 50:
            add([("Windproof outer layer", RECOMMENDED,
                  f"gusts to {gust:.0f} km/h forecast")], wx_items)
        if wet_days:
            add([("Umbrella - small, for town only", OPTIONAL,
                  "useless in wind, fine walking between restaurants")], wx_items)
        sections.append({"section": "Because of the forecast", "items": wx_items,
                         "note": "; ".join(f"{d}: {v['summary']}"
                                           for d, v in sorted(forecast.items()))})
    else:
        add([("Check the forecast before you pack", ESSENTIAL,
              "the trip is outside the 16-day forecast horizon")], wx_items)
        sections.append({"section": "Because of the forecast", "items": wx_items,
                         "note": "No forecast available yet for these dates."})

    # ---------------- activities ----------------
    act_items = []
    for pattern, items in ACTIVITY_GEAR:
        if _matches(pattern, blob):
            add(items, act_items)
        elif _matches(pattern, bench_blob):
            # On the bench, not on the plan: soften both the wording and the
            # priority, so the reader can decide whether to carry it.
            softened = [(name, OPTIONAL if prio == ESSENTIAL else prio,
                         why.replace("you have a ski day scheduled",
                                     "a ski day is on your bench, not your plan")
                            .replace("ski day", "ski day (bench option)")
                            .replace("is on the plan", "is on your bench")
                            .replace("there is walking on the plan",
                                     "walking options are on your bench")
                         + " - only if you take that option")
                        for name, prio, why in items]
            add(softened, act_items)
    if has_outdoor and not any("walking shoes" in i["item"].lower() for i in act_items):
        add([("Comfortable walking shoes", ESSENTIAL, "there are outdoor stops on the plan")],
            act_items)
    if act_items:
        sections.append({"section": "Because of what is on the itinerary", "items": act_items,
                         "note": "Derived from your scheduled stops. Items marked "
                                 "'only if you take that option' come from bench "
                                 "alternates, not the plan itself."})

    # ---------------- documents ----------------
    doc_items = []
    if has_fixed_car:
        add([("Driver's licence for every driver", ESSENTIAL,
              "you are collecting a rental car"),
             ("The card the rental booking was made on", ESSENTIAL,
              "rental desks hold a bond against it"),
             ("International Driving Permit if your licence is not in English",
              ESSENTIAL, "New Zealand requires it alongside the licence"),
             ("Phone mount and a charging cable for the car", RECOMMENDED,
              "navigation on unfamiliar roads")], doc_items)
    if has_flight:
        add([("Passport or photo ID", ESSENTIAL, "you have flights either end"),
             ("Boarding passes saved offline", RECOMMENDED, "patchy signal in the valley")],
            doc_items)
    add([("Accommodation address and check-in details", ESSENTIAL,
          f"check-in at {brief.get('base', {}).get('name', 'your accommodation')}"),
         ("Booking confirmations for anything pre-paid", ESSENTIAL,
          "activity operators ask at the desk"),
         ("Offline map of the region downloaded", RECOMMENDED,
          "mobile coverage drops out on the mountain roads")], doc_items)
    sections.append({"section": "Documents and admin", "items": doc_items})

    # ---------------- basics ----------------
    n = int(brief.get("days", 0) or 0)
    basics = []
    add([(f"Type I plug adaptor", ESSENTIAL,
          "New Zealand uses Type I sockets, 230 V"),
         ("Power bank", RECOMMENDED, "cold drains phone batteries fast"),
         (f"Clothing for {n} days plus one", RECOMMENDED,
          "one spare set covers the day something gets soaked"),
         ("Any prescription medication", ESSENTIAL, "pharmacies keep short hours"),
         ("Reusable water bottle", OPTIONAL, "tap water is drinkable everywhere"),
         ("Lip balm", OPTIONAL, "cold, dry, high-altitude air")], basics)
    sections.append({"section": "Basics", "items": basics})

    drop_items = [x.lower() for x in (brief.get("packing_exclude") or [])]
    drop_sections = [x.lower() for x in (brief.get("packing_exclude_sections") or [])]
    pruned = []
    for sec in sections:
        if any(k in sec["section"].lower() for k in drop_sections):
            continue
        sec = dict(sec)
        sec["items"] = [i for i in sec["items"]
                        if not any(k in i["item"].lower() for k in drop_items)]
        pruned.append(sec)
    return [s for s in pruned if s["items"]]
