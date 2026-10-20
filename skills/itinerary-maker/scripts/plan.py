#!/usr/bin/env python3
"""Phase 3+4: score candidates, build mixable day options, schedule them.

The output is deliberately NOT one itinerary. It is a set of self-contained
day options - each one a closed loop that starts and ends at your accommodation
- so any day can be swapped for any other without breaking the geography. Pick
Day 1 from option A and Day 2 from option B and the plan still works.

Every scheduled stop also carries a bench: two or three alternates tagged with
why you would swap (rain, closed, too tired, running late, cheaper), chosen to
sit in the same area and take about the same time so a swap does not cascade
through the rest of the day.

Usage:
  plan.py --trip SLUG [--options-per-day 4] [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import geo       # noqa: E402
import sun       # noqa: E402
import weather as wx  # noqa: E402
import packing   # noqa: E402
import money     # noqa: E402

# Pace controls how much of the day you are willing to spend moving, and how
# much slack sits between stops. An itinerary packed to 100% fails at stop two.
PACE = {
    "relaxed":  {"start": 9 * 60,    "end": 19 * 60,      "slack": 0.30, "max_stops": 3},
    "moderate": {"start": 8 * 60 + 30, "end": 20 * 60,    "slack": 0.20, "max_stops": 5},
    "packed":   {"start": 7 * 60 + 30, "end": 21 * 60 + 30, "slack": 0.12, "max_stops": 7},
}

# Slack is a percentage, but capped: 20% of a 3.5-hour drive is 42 minutes of
# padding on a leg whose duration is already known to the minute.
MAX_SLACK_PER_LEG_MIN = 20

# Waiting two hours for a gallery to open is not a plan, it is a hostage
# situation. Past this, the stop goes to the bench instead.
MAX_WAIT_MIN = 75

# How far a day is allowed to spread, by how you are getting around. A car
# forgives a bad cluster; walking does not. Without this, a Lisbon walking day
# strung four high-scoring museums across the city with 86-minute legs between
# them - each stop excellent, the day unusable.
SPREAD_KM = {"pedestrian": 2.5, "bicycle": 9.0, "auto": 45.0}

MEALS = [("Lunch", 12 * 60, 14 * 60 + 30, 60),
         ("Dinner", 18 * 60, 20 * 60 + 30, 90)]

# Theme keywords. A candidate can carry several; a day option is named after
# whichever theme dominates its stops.
THEMES = {
    "adrenaline": r"\b(bungy|bungee|skydiv|jet ?boat|raft|luge|zipline|canyon|paraglid|"
                  r"speed|extreme|adventure|quad|off-?road)\b",
    "scenic":     r"\b(view|viewpoint|lookout|scenic|panoram|summit|peak|lake|fiord|"
                  r"sound|glacier|mountain|gondola|cruise|drive|vista)\b",
    "walking":    r"\b(walk|hike|track|trail|stroll|loop|reserve|garden|park)\b",
    "food":       r"\b(restaurant|cafe|café|eat|dining|food|burger|brunch|bakery)\b",
    "wine":       r"\b(wine|winery|vineyard|cellar|brewery|distiller|beer|gin|tasting)\b",
    "culture":    r"\b(museum|gallery|historic|heritage|maori|māori|art|theatre|"
                  r"cinema|library|church|goldfield|settlement)\b",
    "snow":       r"\b(ski|snowboard|snow|alpine|ice|glacier|field)\b",
    "relax":      r"\b(spa|hot pool|thermal|massage|onsen|sauna|beach|picnic)\b",
    "family":     r"\b(kids|children|family|playground|zoo|farm|animal|maze)\b",
}


# --------------------------------------------------------------------------
# opening hours - a light parse that admits what it does not know
# --------------------------------------------------------------------------
CLOSED_SEASON = re.compile(
    r"\b(closed (in |during )?(the )?winter|summer only|seasonal|"
    r"closed (jun|jul|aug|sep|may)|winter only|nov[\-\u2013]|open (oct|nov|dec)[\-\u2013])\b", re.I)

# One time token: 9, 9:30, 9.30, 17:00, each optionally followed by am/pm.
# Written to require a word boundary BEFORE the hour, because an earlier
# version happily read the '30' out of '9:30 am' as the opening hour and
# scheduled a gallery to open at 30:00.
TIME_TOKEN = re.compile(
    r"(?<![\d:.])(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)?(?![\d:.])", re.I)


def _to_minutes(hour: int, minute: int, meridiem: str | None):
    if meridiem:
        m = meridiem.lower().replace(".", "")
        if m == "pm" and hour != 12:
            hour += 12
        elif m == "am" and hour == 12:
            hour = 0
    if not (0 <= hour <= 24 and 0 <= minute < 60):
        return None
    return hour * 60 + minute


def parse_hours(text: str):
    """(opens_min, closes_min, confidence). Unknown stays unknown.

    OSM and Wikivoyage hours strings are free-form enough that a confident
    parser would be a liar. This finds the obvious cases, validates the result
    against the clock, and shrugs at the rest.
    """
    if not text or not text.strip():
        return None, None, "unknown"
    t = text.strip()
    low = t.lower()
    if low in ("24/7", "24 hours", "24hrs", "always", "always open"):
        return 0, 24 * 60, "high"

    times = []
    for m in TIME_TOKEN.finditer(t):
        hour = int(m.group(1))
        minute = int(m.group(2) or 0)
        val = _to_minutes(hour, minute, m.group(3))
        if val is not None:
            times.append((val, bool(m.group(3)), m.group(2) is not None))
    if len(times) < 2:
        return None, None, "unknown"

    opens, closes = times[0][0], times[1][0]

    # '9 am - 5' almost always means 5 in the afternoon.
    if closes <= opens and not times[1][1]:
        closes += 12 * 60
    # Late-night venues legitimately close after midnight.
    if closes <= opens:
        closes += 24 * 60

    if not (0 <= opens < 24 * 60) or not (opens < closes <= 30 * 60):
        return None, None, "unknown"

    span = closes - opens
    if span < 30 or span > 20 * 60:
        return None, None, "unknown"      # nonsense range, admit ignorance

    conf = "medium" if times[0][2] or times[0][1] else "low"
    return opens, closes, conf


WEEKDAY_NAMES = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}


def available_on(c: dict, date) -> bool:
    """False when a candidate only runs on days this date is not.

    Coronet Peak's night ski runs Wednesdays and Fridays. Left unfiltered it
    sat in Tuesday's pool, consumed the evening in the scheduler's arithmetic,
    and helped push the actual ski day off the end of the clock.
    """
    days = c.get("only_weekdays")
    if not days:
        return True
    wanted = {WEEKDAY_NAMES.get(str(x).strip().lower()[:3], -1) for x in days}
    return date.weekday() in wanted


def seasonal_risk(c: dict, month: int) -> bool:
    """True when the source hints this may not run in the traveller's month."""
    blob = " ".join(str(c.get(k, "")) for k in ("hours", "desc", "price", "name"))
    if CLOSED_SEASON.search(blob):
        return True
    return False


# --------------------------------------------------------------------------
# scoring
# --------------------------------------------------------------------------
# Where a place is, for grouping the food list. The base town gets the full
# list because you are living there for three days; everywhere else is
# somewhere you pass through, and one highlight is the right depth.
TOWNS = [
    ("Queenstown", -45.0312, 168.6626), ("Frankton", -45.0197, 168.7000),
    ("Arrowtown", -44.9394, 168.8330), ("Gibbston", -45.0086, 168.9403),
    ("Wanaka", -44.7032, 169.1321), ("Glenorchy", -44.8497, 168.3852),
    ("Te Anau", -45.4144, 167.7180),
]


def area_for(lat, lon, default="Further afield"):
    if lat is None or lon is None:
        return default
    best, best_km = default, 1e9
    for name, tlat, tlon in TOWNS:
        km = geo.haversine_km((lat, lon), (tlat, tlon))
        if km < best_km:
            best, best_km = name, km
    return best if best_km <= 12 else default


def tag_themes(c: dict) -> list[str]:
    """Themes for a candidate. An explicit list from research always wins.

    Keyword tagging reads the description too, which is usually right and
    occasionally absurd: a winery whose blurb mentions the road to the bungy
    bridge came back tagged 'adrenaline'. So the name is weighted, the
    description is only consulted for themes the name did not settle, and
    anything the research layer states outright is taken as given.
    """
    if c.get("themes_explicit"):
        return list(c["themes_explicit"])
    name = f"{c.get('name','')} {c.get('osm_kind','')}"
    from_name = {t for t, pat in THEMES.items() if re.search(pat, name, re.I)}
    if from_name:
        return sorted(from_name)
    desc = (c.get("desc") or "")[:300]
    return sorted({t for t, pat in THEMES.items() if re.search(pat, desc, re.I)})


# Overpass names things the way a surveyor does, not the way a traveller does.
# 'above paragliding spot' and 'Historic reserve' are map labels, not places you
# can decide to go to.
JUNK_NAME = re.compile(
    r"^(above |below |near |old |derelict|ruins?$|site of|unnamed|track|path|"
    r"historic reserve$|scenic reserve$|reserve$|car ?park|toilets?$|shelter$|"
    r"lookout$|viewpoint$|hut$|bridge$|memorial$)", re.I)


# Places that exist in every town and that nobody travels to see. Overpass
# tags them the same way it tags a museum, so they have to be named explicitly.
NOT_AN_ATTRACTION = re.compile(
    r"\b(library|supermarket|four ?square|pak ?n ?save|woolworths|new world|"
    r"countdown|petrol|service station|pharmacy|medical|hospital|school|"
    r"police|post office|bank|atm|laundry|car ?rental|i-?site|information centre|"
    r"cinema|movie theat|bowling|gym|fitness)\b", re.I)


def is_junk(name: str) -> bool:
    n = (name or "").strip()
    if len(n) < 3:
        return True
    if n[0].islower():            # a real place name is capitalised
        return True
    return bool(JUNK_NAME.match(n))


GENERIC = re.compile(
    r"^(cycling|walking|hiking|horseback riding|fishing( and flyfishing)?|"
    r"skiing|golf|shopping|swimming|running|climbing|tramping|boating)$", re.I)


def score(c: dict, brief: dict) -> tuple[float, list[str]]:
    """Score a candidate, and say why. The reasons end up in the spreadsheet."""
    why = []
    s = 0.0

    # Substance: a listing somebody bothered to describe is a real attraction.
    desc_len = len(c.get("desc", "")) + len(c.get("wikipedia_extract", ""))
    if desc_len > 400:
        s += 3.0; why.append("well documented")
    elif desc_len > 120:
        s += 1.8
    elif desc_len > 0:
        s += 0.8
    if c.get("image"):
        s += 1.2; why.append("has photo")
    if c.get("source") == "wikivoyage":
        s += 1.5
    if c.get("source") == "agent-research":
        # Research entries exist because somebody went looking for them. That
        # deliberateness is signal: without this, the Milford Sound cruise -
        # the entire reason anyone drives to Milford Sound - scored below a
        # small-town art gallery, because the gallery had a longer blurb.
        s += 3.5; why.append("added by research")
    if c.get("corrected_by_agent"):
        s += 1.0; why.append("price/hours checked")
    if c.get("url"):
        s += 0.6

    # Interest match against what the traveller actually asked for.
    themes = c.get("themes", [])
    wanted = set(brief.get("interests", []))
    hits = wanted & set(themes)
    if hits:
        s += 2.2 * len(hits)
        why.append("matches " + "/".join(sorted(hits)))
    elif wanted and themes:
        s -= 0.8

    # Penalties.
    if GENERIC.match(c.get("name", "").strip()):
        s -= 5.0; why.append("generic category, not a bookable stop")
    if is_junk(c.get("name", "")):
        s -= 6.0; why.append("map label rather than a destination")
    if NOT_AN_ATTRACTION.search(c.get("name", "")):
        s -= 6.0; why.append("everyday amenity, not somewhere you travel to see")
    if c.get("located_by") == "UNLOCATED":
        s -= 3.0; why.append("could not be located")
    if c.get("source") == "overpass" and not c.get("desc"):
        s -= 1.5
    if c.get("seasonal_risk"):
        s -= 2.5; why.append("may be closed this season")

    # Reachability from base.
    km = c.get("km_from_centre")
    if km is not None:
        if km > 200:
            s -= 2.0
        elif km > 80:
            s -= 0.8
    return round(s, 2), why


# --------------------------------------------------------------------------
# ordering + scheduling
# --------------------------------------------------------------------------
def best_order(stops, base_pt, g, mode):
    """Cheapest visiting order. Exhaustive while that is affordable."""
    if len(stops) <= 1:
        return stops

    def leg(a, b):
        r = g.route(a, b, mode)
        return r["mins"] if r else 999

    pts = [(s["lat"], s["lon"]) for s in stops]
    if len(stops) <= 6:
        best, best_cost = None, float("inf")
        for perm in itertools.permutations(range(len(stops))):
            cost = leg(base_pt, pts[perm[0]])
            for a, b in zip(perm, perm[1:]):
                cost += leg(pts[a], pts[b])
            cost += leg(pts[perm[-1]], base_pt)
            if cost < best_cost:
                best, best_cost = perm, cost
        return [stops[i] for i in best]

    # Nearest neighbour once the factorial stops being a good idea.
    remaining = list(range(len(stops)))
    order, cur = [], base_pt
    while remaining:
        nxt = min(remaining, key=lambda i: leg(cur, pts[i]))
        order.append(nxt)
        remaining.remove(nxt)
        cur = pts[nxt]
    return [stops[i] for i in order]


def nearest_dining(near, dining, label, n=3, radius_km=25, after_dark=False):
    """The closest few places from the traveller's own list that suit this meal.

    Offering three beats committing to one. Nothing on a trip like this is
    booked in advance, plans move during the day, and a single auto-assigned
    restaurant is both more fragile and less useful than a short list you can
    choose from while standing in the street.
    """
    out = []
    for c in dining:
        if c.get("lat") is None:
            continue
        meal = (c.get("meal") or "").lower()
        if label == "Dinner" and meal in ("breakfast", "lunch"):
            continue
        if label == "Lunch" and meal == "dinner":
            continue
        if label in ("Lunch", "Dinner") and (c.get("kind") == "drink" or meal == "drinks"):
            continue
        km = geo.haversine_km(near, (c["lat"], c["lon"]))
        if km > radius_km:
            continue
        penalty = 6.0 if (after_dark and not c.get("indoor", True)) else 0.0
        bonus = -3.0 if meal == label.lower() else 0.0
        out.append((km * 0.6 + penalty + bonus - c.get("score", 0), km, c))
    out.sort(key=lambda x: x[0])
    return [{"name": c["name"], "km": round(km, 1), "price": c.get("price", ""),
             "area": c.get("area", ""),
             "price_nzd": c.get("price_nzd"), "url": c.get("url", ""),
             "maps_query": c.get("maps_query", ""),
             "lat": c.get("lat"), "lon": c.get("lon"),
             "desc": (c.get("desc") or "")[:150], "indoor": c.get("indoor", True)}
            for _, km, c in out[:n]]


def pick_dining(near, dining, used, g, mode, label, radius_km=12,
                after_dark=False, cold=False):
    """The best place to eat that is actually near where you will be.

    Restaurants are not sights. An earlier version scheduled five of them in a
    row as if they were, producing a day that started with steak at 08:32.
    """
    best, best_key = None, None
    tried = radius_km
    for c in dining:
        if c["name"] in used or c.get("lat") is None:
            continue
        km = geo.haversine_km(near, (c["lat"], c["lon"]))
        if km > radius_km:
            continue

        key = -c.get("score", 0) + km * 0.6

        # Respect what the place is FOR. Serving a breakfast roastery as dinner
        # is not a suggestion, it is a mistake with a link attached.
        meal = (c.get("meal") or "").lower()
        if meal:
            if meal == label.lower():
                key -= 4.0
            elif label == "Dinner" and meal in ("breakfast", "lunch"):
                continue
            elif label == "Lunch" and meal == "breakfast":
                key += 3.0

        # A bar is a drink, not a dinner. It can still fill an evening slot,
        # but it should not beat an actual restaurant to one.
        # A bar is drinks, not dinner. Penalising it was not enough - with a
        # short shortlist a rooftop bar still won a 3-degree Monday evening.
        if c.get("kind") == "drink" or (c.get("meal") or "").lower() == "drinks":
            continue
        # A rooftop terrace is a poor dinner in the dark at 6 degrees.
        if after_dark and c.get("weather_sensitive") and not c.get("indoor"):
            key += 8.0
        elif cold and not c.get("indoor"):
            key += 3.0
        # Where to eat is pure taste, and the traveller's own research is the
        # only source that knows theirs. A gazetteer listing should not beat a
        # place they went and found for themselves, so this weight is large on
        # purpose - larger than it would be for a sight.
        if c.get("source") == "agent-research":
            key -= 9.0

        if best_key is None or key < best_key:
            best, best_key = c, key
    if best is None and radius_km < 60:
        # Nothing within reach - look further out before giving up. On the
        # Glenorchy road every option is 45 km behind you, and "(none)" helps
        # nobody standing in a car park at one o'clock.
        return pick_dining(near, dining, used, g, mode, label,
                           radius_km=min(60, radius_km * 3),
                           after_dark=after_dark, cold=cold)
    return best


def schedule_day(stops, brief, base_pt, date, g, mode, pace, dawn_start=False,
                 dining=None, used_names=None, fixed=None, window=None, weather=None):
    """Walk the clock through a day, around whatever is already nailed down.

    Fixed items - a landing time, a check-in, a booked tour, a flight home -
    are placed at their stated times and never moved. Everything flexible is
    fitted into the gaps between them, which is the only honest way to schedule
    a travel day: the plane lands when it lands.

    Anything that cannot fit is dropped with a reason rather than silently
    scheduled into the dark, and comes back as a bench candidate instead.
    """
    lat, lon = base_pt
    rise, set_ = sun.sun_times(lat, lon, date, brief.get("utc_offset_hours", 12))
    if rise is None or set_ is None:
        rise, set_ = 6 * 60, 20 * 60          # extreme latitude: fall back

    p = PACE[pace]
    earliest = (rise - 45) if dawn_start else p["start"]
    day_start = max(earliest, rise - 45 if dawn_start else rise - 20)
    hard_end = p["end"] + (150 if dawn_start else 0)
    if window:
        if window[0] is not None:
            day_start = window[0]
        if window[1] is not None:
            hard_end = window[1]

    dining = dining or []
    used_names = used_names if used_names is not None else set()
    anchors = sorted(fixed or [], key=lambda a: a["start"])

    # On a genuinely wet day, indoor options go first. The outdoor stops are
    # not deleted - they stay on the bench - but they stop leading the day.
    band = (weather or {}).get("band", "good")
    if band in ("wet", "snow"):
        stops = sorted(stops, key=lambda c: (not c.get("indoor", False),
                                             -c.get("score", 0)))

    state = {"t": day_start, "prev": base_pt, "travel": 0.0,
             "meals": set(), "timeline": [], "dropped": []}
    remaining = list(stops)
    dining_used = set()

    def place_flexible(limit_t, next_pt):
        """Fill time up to limit_t, leaving room to reach next_pt."""
        for s in list(remaining):
            if s.get("lat") is None:
                continue
            t_before = state["t"]
            tl_before = len(state["timeline"])
            meals_before = set(state["meals"])
            travel_before = state["travel"]

            def rollback():
                state["t"] = t_before
                state["travel"] = travel_before
                state["meals"] = set(meals_before)
                del state["timeline"][tl_before:]

            leg = g.route(state["prev"], (s["lat"], s["lon"]), mode) \
                or {"mins": 0, "km": 0, "how": "unknown"}
            state["t"] += leg["mins"] + min(leg["mins"] * p["slack"], MAX_SLACK_PER_LEG_MIN)
            state["travel"] += leg["mins"]

            for label, lo, hi, dur in MEALS:
                if label not in state["meals"] and lo <= state["t"] <= hi:
                    # Offer the nearest few from the traveller's own list rather
                    # than commit to one. Nothing is booked, plans move, and three
                    # you can choose between beats one picked for you.
                    opts = nearest_dining(state["prev"], dining, label,
                                          after_dark=state["t"] > set_)
                    entry = {"type": "meal", "name": label, "start": round(state["t"]),
                             "end": round(state["t"] + dur), "duration_min": dur,
                             "options": opts}
                    if opts:
                        spot = opts[0]
                        entry.update({"suggestion": spot["name"],
                                      "suggestion_price": spot.get("price", ""),
                                      "suggestion_url": spot.get("url", ""),
                                      "suggestion_desc": spot.get("desc", ""),
                                      "maps_query": spot.get("maps_query", ""),
                                      "price_nzd": spot.get("price_nzd"),
                                      "lat": spot.get("lat"), "lon": spot.get("lon")})
                    state["timeline"].append(entry)
                    state["t"] += dur
                    state["meals"].add(label)

            opens, closes, hconf = parse_hours(s.get("hours", ""))
            if opens is not None and state["t"] < opens:
                wait = opens - state["t"]
                if wait > MAX_WAIT_MIN:
                    state["dropped"].append({**s, "drop_reason":
                                             f"opens {sun.hhmm(opens)}, a {round(wait)} min wait"})
                    rollback()
                    continue
                state["timeline"].append({"type": "wait",
                                          "name": f"{s['name']} opens at {sun.hhmm(opens)}",
                                          "start": round(state["t"]), "end": opens,
                                          "duration_min": round(wait)})
                state["t"] = opens

            dur = s.get("duration_min") or 60
            fin = state["t"] + dur

            if closes is not None and fin > closes:
                state["dropped"].append({**s, "drop_reason":
                                         f"closes {sun.hhmm(closes)}, you would arrive "
                                         f"{sun.hhmm(state['t'])}"})
                rollback(); continue
            if s.get("weather_sensitive") and not s.get("indoor") and fin > set_:
                state["dropped"].append({**s, "drop_reason":
                                         f"outdoor, and sunset is {sun.hhmm(set_)}"})
                rollback(); continue
            if band == "snow" and s.get("weather_sensitive") and not s.get("indoor") \
                    and (weather or {}).get("rain_mm", 0) >= 20:
                state["dropped"].append({**s, "drop_reason":
                                         f"outdoor, and the forecast is "
                                         f"{weather['description'].lower()} with "
                                         f"{weather['rain_mm']:.0f} mm"})
                rollback(); continue

            onward = g.route((s["lat"], s["lon"]), next_pt, mode) or {"mins": 0}
            if fin + onward["mins"] > limit_t:
                state["dropped"].append({**s, "drop_reason":
                                         f"would not leave time to reach the next fixed "
                                         f"item by {sun.hhmm(limit_t)}"
                                         if anchors else "day is full"})
                rollback(); continue

            state["timeline"].append({
                "type": "stop", "name": s["name"], "start": round(state["t"]),
                "end": round(fin), "duration_min": dur,
                "travel_mins": round(leg["mins"]), "travel_km": leg["km"],
                "travel_how": leg["how"], "lat": s["lat"], "lon": s["lon"],
                "price": s.get("price", ""), "price_nzd": s.get("price_nzd"),
                "maps_query": s.get("maps_query", ""),
                "hours": s.get("hours", ""),
                "hours_confidence": hconf, "url": s.get("url", ""),
                "image": s.get("image", ""), "desc": s.get("desc", "")[:400],
                "indoor": s.get("indoor", False),
                "weather_sensitive": s.get("weather_sensitive", False),
                "stale": s.get("stale", True), "source": s.get("source", ""),
                "source_years_old": s.get("source_years_old"),
                "themes": s.get("themes", []), "score": s.get("score", 0),
                "day_trip_hub": s.get("day_trip_hub", ""),
                "located_by": s.get("located_by", ""),
                "kind": s.get("kind", ""),
            })
            state["t"] = fin
            state["prev"] = (s["lat"], s["lon"])
            remaining.remove(s)

    for a in anchors:
        a_pt = (a.get("lat"), a.get("lon"))
        if a_pt[0] is None:
            a_pt = base_pt
        place_flexible(a["start"], a_pt)
        leg = g.route(state["prev"], a_pt, mode) or {"mins": 0, "km": 0, "how": "unknown"}
        state["travel"] += leg["mins"]
        state["timeline"].append({
            "type": "fixed", "name": a["name"], "start": a["start"], "end": a["end"],
            "duration_min": a["end"] - a["start"], "travel_mins": round(leg["mins"]),
            "travel_km": leg.get("km", 0), "travel_how": leg.get("how", "unknown"),
            "lat": a_pt[0], "lon": a_pt[1], "note": a.get("note", ""),
            "price_nzd": a.get("price_nzd"),
            "link_to": a.get("link_to", ""), "link_label": a.get("link_label", ""),
            "url": a.get("url", ""), "image": a.get("image", ""),
            "desc": a.get("desc", ""), "indoor": a.get("indoor", True),
            "price": a.get("price", ""), "soft": bool(a.get("soft")),
            "bare": bool(a.get("bare")),
        })
        state["t"] = max(state["t"], a["end"])
        state["prev"] = a_pt

    ends_at_base = not anchors or not anchors[-1].get("terminal")
    place_flexible(hard_end, base_pt if ends_at_base else state["prev"])

    if ends_at_base:
        back = g.route(state["prev"], base_pt, mode) or {"mins": 0, "km": 0, "how": "unknown"}
        state["travel"] += back["mins"]
        state["t"] += back["mins"]
        state["timeline"].append({"type": "return", "name": "Back to base",
                                  "start": round(state["t"] - back["mins"]),
                                  "end": round(state["t"]), "travel_mins": round(back["mins"]),
                                  "travel_km": back["km"], "travel_how": back["how"]})

    # Dinner gets appended if the day never happened to run through the dinner
    # window. Days that end at 17:40 were producing no dinner suggestion at
    # all, which is not how anybody's evening actually goes.
    terminal_day = bool(anchors) and anchors[-1].get("terminal")
    # A fixed evening commitment IS dinner. Appending another one produced a
    # second dinner at 21:43, after the first had finished.
    FOODY = re.compile(r"\b(dinner|lunch|eat|restaurant|cafe|caf\u00e9|bar|kitchen|"
                       r"burger|pizza|tavern|brew|dine|dining|supper|meal)\b", re.I)
    evening_taken = any(a["end"] > 17 * 60 + 30 and a["start"] < 21 * 60
                        and FOODY.search(a["name"]) for a in anchors)
    if "Dinner" not in state["meals"] and not terminal_day and not evening_taken and dining:
        # Searched from base, not from the last stop: an appended dinner comes
        # after you have driven home. Anchoring it to a lookout 15 km out of
        # town found nothing at all and served no dinner.
        opts = nearest_dining(base_pt, dining, "Dinner", after_dark=True)
        if opts:
            start_t = max(state["t"] + 30, 18 * 60 + 30)
            # Only a track with an explicit finish blocks a late dinner; the
            # pace setting's end time is about activities, not supper.
            explicit_end = bool(window and window[1] is not None)
            if not (explicit_end and start_t + 90 > hard_end):
                spot = opts[0]
                state["timeline"].append({
                    "type": "meal", "name": "Dinner", "start": round(start_t),
                    "end": round(start_t + 90), "duration_min": 90, "options": opts,
                    "suggestion": spot["name"], "suggestion_price": spot.get("price", ""),
                    "suggestion_url": spot.get("url", ""),
                    "suggestion_desc": spot.get("desc", ""),
                    "maps_query": spot.get("maps_query", ""),
                    "price_nzd": spot.get("price_nzd"),
                    "lat": spot.get("lat"), "lon": spot.get("lon"), "appended": True})

    for s in remaining:
        if not any(dd["name"] == s["name"] for dd in state["dropped"]):
            state["dropped"].append({**s, "drop_reason": "no room left in the day"})

    t = state["t"]
    stats = {
        "sunrise": sun.hhmm(rise), "sunset": sun.hhmm(set_),
        "daylight_hours": round((set_ - rise) / 60, 1),
        "starts": sun.hhmm(day_start), "ends": sun.hhmm(t),
        "travel_mins": round(state["travel"]),
        "stops": sum(1 for x in state["timeline"] if x["type"] == "stop"),
        "fixed_items": sum(1 for x in state["timeline"] if x["type"] == "fixed"),
        "after_dark": t > set_,
        "day_length_hours": round((t - day_start) / 60, 1),
    }
    if weather:
        stats["weather"] = weather
    return state["timeline"], state["dropped"], stats


# --------------------------------------------------------------------------
# day options
# --------------------------------------------------------------------------
def bench_for(stop, pool, g, mode, n=3):
    """Alternates for one stop: same area, similar length, tagged by why.

    Deliberately not 'the next best thing in town' - a bench pick two hours
    away is not a substitute for anything.
    """
    out = []
    here = (stop["lat"], stop["lon"])
    for c in pool:
        if c["name"] == stop["name"] or c.get("lat") is None:
            continue
        km = geo.haversine_km(here, (c["lat"], c["lon"]))
        if km > 25:
            continue
        dur_gap = abs((c.get("duration_min") or 60) - (stop.get("duration_min") or 60))
        if dur_gap > 75:
            continue

        # A bench pick has to be a plausible substitute, not merely nearby.
        # Offering a steakhouse as the alternate to a jet boat helps nobody.
        stop_themes = set(stop.get("themes", []))
        cand_themes = set(c.get("themes", []))
        shared = stop_themes & cand_themes
        rain_swap = stop.get("weather_sensitive") and c.get("indoor")
        if not shared and not rain_swap:
            continue
        if c.get("kind") in ("eat", "drink", "buy") and stop.get("kind") not in ("eat", "drink", "buy"):
            continue

        reasons = []
        if stop.get("weather_sensitive") and c.get("indoor"):
            reasons.append("if it rains")
        if c.get("indoor") and not stop.get("indoor"):
            reasons.append("indoor swap")
        if (c.get("duration_min") or 60) < (stop.get("duration_min") or 60) - 25:
            reasons.append("if you are running late")
        if not c.get("price") and stop.get("price"):
            reasons.append("likely cheaper")
        if shared:
            reasons.append("also " + "/".join(sorted(shared)))
        if not reasons:
            reasons.append("same area, different flavour")

        out.append({
            "name": c["name"], "why": reasons, "km_away": round(km, 1),
            "duration_min": c.get("duration_min"), "price": c.get("price", ""),
            "indoor": c.get("indoor", False), "url": c.get("url", ""),
            "image": c.get("image", ""), "score": c.get("score", 0),
            "desc": c.get("desc", "")[:220], "themes": sorted(cand_themes),
        })
    out.sort(key=lambda x: (-len([r for r in x["why"] if r != "same area, different flavour"]),
                            -x["score"], x["km_away"]))
    return out[:n]


def build_options(cands, brief, base_pt, dates, g, mode, pace, per_day):
    """Generate self-contained day options, each a closed loop from base.

    Every option starts and ends at your accommodation, which is what makes
    them mixable: take Day 1 from one option and Day 2 from another and the
    geography still holds.
    """
    options = []
    p = PACE[pace]
    date0 = dates[0]

    # Places to eat are not sights. They are held back and dropped into the
    # meal slots of whatever day you end up choosing.
    dining = [c for c in cands if c.get("kind") in ("eat", "drink")
              and c.get("lat") is not None]
    if brief.get("dining_only_mine"):
        mine = [c for c in dining if c.get("source") == "agent-research"]
        if mine:
            dining = mine
    sights = [c for c in cands if c.get("kind") not in ("eat", "drink", "buy")]

    def cluster(ranked, mode, limit):
        """Keep the best stop, then only what sits within reach of it."""
        if not ranked:
            return []
        seed = ranked[0]
        reach = SPREAD_KM.get(mode, 45.0)
        near = [c for c in ranked
                if geo.haversine_km((seed["lat"], seed["lon"]), (c["lat"], c["lon"])) <= reach]
        return near[:limit]

    def make(oid, title, kind, hub, pool, picks, dawn):
        picks = best_order(picks, base_pt, g, mode)
        tl, dropped, stats = schedule_day(picks, brief, base_pt, date0, g, mode,
                                          pace, dawn_start=dawn, dining=dining)
        if stats["stops"] == 0:
            return None
        rt = round(pool[0].get("hub_drive_mins") * 2) if hub and pool[0].get("hub_drive_mins") \
            else stats["travel_mins"]
        return {
            "id": oid, "title": title, "kind": kind, "hub": hub,
            "theme": dominant_theme(picks),
            "driving_round_trip_mins": rt,
            "timeline": tl, "dropped": dropped, "stats": stats,
            "warnings": hub_warnings(rt, stats, tl) if hub else
                        ([f"you get back after sunset ({stats['sunset']})"]
                         if stats.get("after_dark") else []),
            "score": round(sum(c["score"] for c in picks), 2),
            "pool": [c["name"] for c in pool],
        }

    # --- day-trip options: one per neighbouring hub ---
    hubs = {}
    for c in sights:
        h = c.get("day_trip_hub")
        if h:
            hubs.setdefault(h, []).append(c)

    for hub, members in sorted(hubs.items()):
        drive = members[0].get("hub_drive_mins")
        if drive is None:
            continue
        ranked = sorted(members, key=lambda c: -c["score"])
        o = make(f"hub-{re.sub(r'[^a-z0-9]+', '-', hub.lower()).strip('-')}",
                 f"{hub} day trip", "day-trip", hub, ranked,
                 ranked[:max(2, p["max_stops"] - 2)], drive >= 60)
        if o:
            o["score"] = round(o["score"] - drive * 2 / 45.0, 2)
            options.append(o)

    # --- local themed loops from the base area ---
    local = [c for c in sights if not c.get("day_trip_hub") and c.get("lat") is not None]
    wanted = [t for t in (brief.get("interests") or list(THEMES)) if t != "food"]
    for theme in wanted:
        pool = [c for c in local if theme in c.get("themes", [])]
        if len(pool) < 2:
            continue
        ranked = sorted(pool, key=lambda c: -c["score"])
        o = make(f"local-{theme}", f"{theme.title()} day around {brief['destination']}",
                 "local", "", ranked, cluster(ranked, mode, p["max_stops"]), False)
        if o:
            options.append(o)

    # --- a mixed 'greatest hits' day, for when no single theme dominates ---
    if local:
        ranked = sorted(local, key=lambda c: -c["score"])
        o = make("local-highlights", f"{brief['destination']} highlights",
                 "local", "", ranked, cluster(ranked, mode, p["max_stops"]), False)
        if o:
            options.append(o)

    options.sort(key=lambda o: -o["score"])
    return options, dining, {c["name"]: c for c in sights}


def dominant_theme(stops):
    counts = {}
    for s in stops:
        for th in s.get("themes", []):
            counts[th] = counts.get(th, 0) + 1
    return max(counts, key=counts.get) if counts else "mixed"


def hub_warnings(round_trip_mins, stats, timeline=None):
    w = []
    # If the day is already built around a guided tour, telling the traveller
    # to consider a guided tour is noise.
    guided = any(re.search(r"\b(guided|coach|tour|shuttle|transfer)\b", i.get("name", ""), re.I)
                 for i in (timeline or []) if i.get("type") == "stop")
    if guided:
        w.append("somebody else is driving on this one - the transport is part of the booking")
    elif round_trip_mins >= 360:
        w.append(f"{round_trip_mins // 60}h {round_trip_mins % 60}m of driving before you see "
                 f"anything - consider a coach or flight so somebody else drives")
    elif round_trip_mins >= 210:
        w.append(f"{round_trip_mins // 60}h {round_trip_mins % 60}m round trip driving - "
                 f"this eats the whole day")
    if stats.get("after_dark"):
        w.append(f"you get back after sunset ({stats['sunset']})")
    if stats.get("day_length_hours", 0) >= 12:
        w.append(f"a {stats['day_length_hours']}h day - do not stack this next to another big one")
    return w


def outdoor_ratio(option):
    """How much of an option is exposed to the weather, 0.0 to 1.0."""
    stops = [i for i in option["timeline"] if i["type"] == "stop"]
    if not stops:
        return 0.0
    exposed = sum(1 for i in stops if i.get("weather_sensitive") and not i.get("indoor"))
    return exposed / len(stops)


def day_capacity(iso, windows, fixed_by_date, pace, track=None):
    """Usable hours on a date, after its window and its fixed commitments.

    Track-aware: the skiers are not committed to the non-skiers' spa booking,
    and counting every group's anchors against every group left the ski day
    with no capacity for a morning it actually had free.
    """
    p = PACE[pace]
    start, end = windows.get(iso, (None, None))
    start = p["start"] if start is None else start
    end = p["end"] if end is None else end
    committed = sum(a["end"] - a["start"] for a in fixed_by_date.get(iso, [])
                    if track is None or not a.get("track") or a.get("track") == track)
    return max(0.0, (end - start - committed) / 60.0)


def day_fit(option, iso, windows, fixed_by_date, forecast, pace):
    """How well an option suits one particular date. Higher is better.

    Selecting options first and dating them afterwards put bungy jumping on a
    95%-rain day and a Wanaka day trip on a departure morning with snow
    forecast. Weather, the day's window and the flight home are properties of
    the DATE, so the pairing has to happen with the date in hand.
    """
    fit = option["score"]
    capacity = day_capacity(iso, windows, fixed_by_date, pace)
    needed = option["stats"].get("day_length_hours", 0)
    terminal = any(a.get("terminal") for a in fixed_by_date.get(iso, []))

    # A day that has to end at an airport is not a day for a long drive out.
    if terminal or capacity < needed:
        drive = option["driving_round_trip_mins"]
        if terminal and drive >= 90:
            return None                      # disqualified, not merely penalised
        fit -= (needed - capacity) * 4.0

    w = forecast.get(iso)
    if w:
        exposure = outdoor_ratio(option)
        if w["band"] == "snow":
            fit -= exposure * 22.0
            if option["hub"] and option["driving_round_trip_mins"] >= 120:
                fit -= 15.0                  # mountain roads, chains, in the dark
        elif w["band"] == "wet":
            fit -= exposure * 14.0
        elif w["band"] == "good":
            fit += exposure * 3.0            # spend the good weather outdoors
    return fit


def day_warnings(option, stats, timeline, weather):
    """Everything worth flagging about one scheduled day, in one place."""
    if option["hub"]:
        w = hub_warnings(option["driving_round_trip_mins"], stats, timeline)
    else:
        w = [f"you get back after sunset ({stats['sunset']})"] \
            if stats.get("after_dark") else []
    if weather:
        w += wx.advice(weather)
    return w


def hhmm_to_min(text):
    """'10:30' -> 630. None stays None."""
    if not text:
        return None
    h, m = str(text).split(":")
    return int(h) * 60 + int(m)


def recommend(options, n_days, brief, base_pt, g, mode, pace, dining, by_name, dates,
              fixed_by_date=None, windows=None, forecast=None):
    """A default mix: highest scoring, varied, and free of repeats.

    This is a suggestion to re-cut, not a verdict. Two rules earn their place:
    variety, because three adrenaline days in a row is a mistake nobody notices
    until day three; and de-duplication, because an option-based plan will
    otherwise cheerfully send you up the same gondola on two different days.
    """
    fixed_by_date = fixed_by_date or {}
    windows = windows or {}
    forecast = forecast or {}

    def stop_names(o):
        return {i["name"] for i in o["timeline"] if i["type"] == "stop"}

    # Anything a fixed anchor already covers must not also be scheduled as a
    # flexible stop. Matched loosely on purpose: the anchor "Skyline Gondola +
    # Luge" covers the candidates "Skyline Gondola" AND "Luge", and an exact
    # name match caught neither - so the plan sent you up the same hill twice.
    STOP_WORDS = {"the", "a", "at", "in", "on", "of", "and", "with", "for", "to"}

    def _tokens(name):
        raw = re.sub(r"[^a-z0-9 ]", " ", (name or "").lower()).split()
        return {t for t in raw if t not in STOP_WORDS and len(t) > 1}

    fixed_token_sets = [_tokens(a["name"])
                        for day in fixed_by_date.values() for a in day]

    def covered_by_fixed(name):
        """Does a fixed anchor already account for this candidate?

        Token overlap, not substring: the anchor "Coronet Peak - afternoon
        pass" and the candidate "Coronet Peak afternoon pass" differ by one
        dash, and substring matching missed it - so the ski day tried to
        schedule the ski field twice and dropped both.
        """
        cand = _tokens(name)
        if not cand:
            return False
        for anc in fixed_token_sets:
            # A one-word name is covered outright if that word is in the
            # anchor: "Luge" is inside "Skyline Gondola + Luge", and requiring
            # two shared tokens sent the group up it a second time.
            if len(cand) == 1 and cand <= anc:
                return True
            shared = cand & anc
            # Two shared significant words AND half the candidate's own words.
            # "Coronet Peak Ski Area" against the anchor "Coronet Peak -
            # afternoon pass" shares two of four; at a 0.6 threshold it slipped
            # through, conflicted with the anchor, got dropped, and left the
            # morning empty because the capacity had already been spent on it.
            if len(shared) >= 2 and len(shared) / len(cand) >= 0.5:
                return True
        return False

    def track_fixed(iso, track_name):
        """Fixed items for this date that apply to this track.

        An anchor with no track belongs to everyone on that date; one naming a
        track belongs only to it - the skiers' 12:30 lift pass is not the
        non-skiers' problem.
        """
        out = []
        for a in fixed_by_date.get(iso, []):
            want = a.get("track")
            if not want or want == track_name:
                out.append(a)
        return out

    def drinking_before(day_fixed, theme_set):
        """True if this day puts alcohol before something you should be sober for.

        Cellar doors before a lift pass is not a plan, it is an incident report.
        """
        risky = any(re.search(r"\b(ski|snowboard|lift pass|coronet|remarkables|"
                              r"bungy|jet ?boat|skydiv|paraglid|heli)\b",
                              a["name"], re.I) for a in day_fixed)
        return risky and bool({"wine"} & set(theme_set))

    def build_day(o, used, idx, slot=None):
        """Schedule one chosen option against what earlier days already took."""
        slot = slot or {"iso": dates[idx].isoformat(), "group": "everyone",
                        "label": "Everyone", "size": None, "primary": True, "note": ""}
        iso = slot["iso"]
        pool = [by_name[n] for n in o["pool"]
                if n in by_name and n not in used and not covered_by_fixed(n)]
        # Backfill replaces what de-duplication removed; it does not turn a
        # three-stop day into a five-stop one, and it will not reach below the
        # quality floor just to fill a gap - an empty afternoon beats a
        # supermarket.
        original = sum(1 for i in o["timeline"] if i["type"] == "stop")
        keep = PACE[pace]["max_stops"]
        floor = 2.0
        ranked_pool = [c for c in sorted(pool, key=lambda c: -c["score"])
                       if c["score"] >= floor]
        reach = SPREAD_KM.get(mode, 45.0)
        picks = ([ranked_pool[0]] + [c for c in ranked_pool[1:]
                 if geo.haversine_km((ranked_pool[0]["lat"], ranked_pool[0]["lon"]),
                                     (c["lat"], c["lon"])) <= reach])[:keep] \
            if ranked_pool else []
        # If the option's own pool leaves a big hole in a constrained day,
        # reach into the wider local pool rather than hand back four idle hours.
        cap = day_capacity(iso, windows, fixed_by_date, pace, slot["group"])
        # A day that is deliberately loose stays loose. Without this, deleting
        # a stop just invites the backfill to substitute another one.
        if slot.get("no_fill"):
            picks, cap = [], 0.0
        # An evening slot is for the thing it was created for. Filling its last
        # hour from the general pool put an art gallery at 20:17.
        if slot.get("window"):
            w0, w1 = (hhmm_to_min(x) for x in slot["window"])
            if w0 is not None and w1 is not None and (w1 - w0) <= 5 * 60:
                cap = 0.0
                picks = []          # an evening out is not a slot to fill
        planned = sum((c.get("duration_min") or 60) for c in picks) / 60.0
        core = list(picks)
        if cap - planned > 2.5:
            seeds = [(picks[0]["lat"], picks[0]["lon"])] if picks else [base_pt]
            seeds += [(a["lat"], a["lon"]) for a in track_fixed(iso, slot["group"])
                      if a.get("lat") is not None]

            def in_reach(c):
                return any(geo.haversine_km(sd, (c["lat"], c["lon"])) <= reach
                           for sd in seeds)
            seed = seeds[0]
            wet = ((forecast.get(iso) or {}).get("band") in ("wet", "snow")
                   and not slot.get("ignore_weather"))
            extras = [c for c in sorted(by_name.values(), key=lambda c: -c["score"])
                      if c["name"] not in {x["name"] for x in picks}
                      and c["name"] not in used
                      and not covered_by_fixed(c["name"])
                      and c.get("lat") is not None and c["score"] >= 2.0
                      and in_reach(c)
                      and (c.get("indoor") or not wet)
                      and not drinking_before(track_fixed(iso, slot["group"]),
                                              c.get("themes", []))]
            picks += extras[:max(0, keep - len(picks))]
        dawn = bool(o["hub"]) and o["driving_round_trip_mins"] >= 120

        # Order the day's own stops first, then the backfill. Optimising the
        # whole list for travel alone let the filler run ahead of the reason
        # for the day: a ski day put two wine stops first and then dropped
        # Coronet Peak because you would have arrived at 21:49.
        picks = [c for c in picks if available_on(c, dates[idx])]
        core = [c for c in core if c in picks]
        extra = [c for c in picks if c not in core]
        picks = best_order(core, base_pt, g, mode)
        if extra:
            tail_from = (picks[-1]["lat"], picks[-1]["lon"]) if picks else base_pt
            picks += best_order(extra, tail_from, g, mode)
        win = (tuple(hhmm_to_min(x) for x in slot["window"])
               if slot.get("window") else windows.get(iso))
        tl, dropped, stats = schedule_day(picks, brief, base_pt, dates[idx], g, mode,
                                          pace, dawn_start=dawn, dining=dining,
                                          used_names=used,
                                          fixed=track_fixed(iso, slot["group"]),
                                          window=win, weather=forecast.get(iso))

        # A day whose every pick was dropped still has its hours. Try again
        # with the wider pool rather than print a blank morning.
        if stats["stops"] == 0 and cap >= 2.5 and not slot.get("no_fill"):
            wet = ((forecast.get(iso) or {}).get("band") in ("wet", "snow")
                   and not slot.get("ignore_weather"))
            rescue = [c for c in sorted(by_name.values(), key=lambda c: -c["score"])
                      if c["name"] not in used and not covered_by_fixed(c["name"])
                      and c.get("lat") is not None and c["score"] >= 2.0
                      and available_on(c, dates[idx])
                      and geo.haversine_km(base_pt, (c["lat"], c["lon"])) <= reach
                      and (c.get("indoor") or not wet)
                      and not drinking_before(track_fixed(iso, slot["group"]),
                                              c.get("themes", []))][:keep]
            if rescue:
                tl, dropped, stats = schedule_day(
                    best_order(rescue, base_pt, g, mode), brief, base_pt, dates[idx],
                    g, mode, pace, dawn_start=dawn, dining=dining, used_names=used,
                    fixed=track_fixed(iso, slot["group"]), window=win,
                    weather=forecast.get(iso))
        out = dict(o)
        out.update({"timeline": tl, "dropped": dropped, "stats": stats,
                    "assigned_day": idx + 1, "date": iso,
                    "group": slot["group"], "group_label": slot["label"],
                    "group_size": slot["size"], "primary": slot["primary"],
                    "track_note": slot.get("note", ""),
                    "choices": slot.get("choices"),
                    "day_title": slot.get("title", ""),
                    "members": slot.get("members", []),
                    "alternative": bool(slot.get("alternative")),
                    "warnings": day_warnings(o, stats, tl, forecast.get(iso))})
        return out

    # Shortlist first, then pair options to dates by fit. Both steps matter:
    # the shortlist keeps the trip varied, the pairing keeps each day sane.
    shortlist, used_themes, used_hubs, big_days = [], set(), set(), 0
    for o in options:
        if len(shortlist) >= n_days + 8:
            break
        if o["hub"] and o["hub"] in used_hubs:
            continue
        if o["theme"] in used_themes and len(options) > n_days + 2:
            continue
        overlap = stop_names(o) & set().union(*[stop_names(c) for c in shortlist]) \
            if shortlist else set()
        if shortlist and len(overlap) >= max(1, len(stop_names(o)) // 2):
            continue
        long_day = (o["driving_round_trip_mins"] >= 240
                    or o["stats"].get("day_length_hours", 0) >= 11)
        if long_day:
            if big_days >= max(1, n_days // 2):
                continue
            big_days += 1
        shortlist.append(o)
        used_themes.add(o["theme"])
        if o["hub"]:
            used_hubs.add(o["hub"])
    for o in options:
        if len(shortlist) >= n_days + 8:
            break
        if o not in shortlist:
            shortlist.append(o)

    # The traveller can nail an option to a date - "ski on the Tuesday". A
    # preference wins over fit, because they have information the scorer does
    # not.
    prefs = {k: str(v).lower() for k, v in (brief.get("day_preferences") or {}).items()}

    # A party does not always stay together. Each date carries one or more
    # tracks - "the skiers", "everyone else" - and each track is planned as its
    # own day. Without this the plan can only describe a group that never
    # splits up, which is not how a group of seven actually travels.
    groups = brief.get("groups") or {}
    track_spec = brief.get("tracks") or {}
    slots = []
    for idx in range(n_days):
        iso = dates[idx].isoformat()
        for t in (track_spec.get(iso) or [{"group": "everyone", "primary": True}]):
            g_key = t.get("group", "everyone")
            # Not `g` - that name is the geocoder in this scope, and shadowing
            # it made best_order try to route with a dictionary.
            gdef = groups.get(g_key, {})
            slots.append({
                "idx": idx, "iso": iso, "group": g_key,
                "label": gdef.get("label", g_key.replace("-", " ").title()),
                "size": gdef.get("size"), "primary": bool(t.get("primary")),
                "prefer": (t.get("prefer") or prefs.get(iso) or "").lower(),
                "note": t.get("note", ""),
                "window": t.get("window"),
                "ignore_weather": bool(t.get("ignore_weather")),
                "no_fill": bool(t.get("no_fill")),
                "choices": t.get("choices"),
                "title": t.get("title", ""),
                # A list, not a name: the Wednesday couple's day has to avoid
                # what BOTH of them already did, and they spent Tuesday apart.
                "lineages": ([str(x) for x in t["lineages"]] if t.get("lineages")
                             else ["primary" if t.get("primary") else g_key]),
                # Who is physically on this track. Separate from `lineages`,
                # which exists for de-duplication: a person's own edition of
                # the itinerary follows the PERSON across every track they are
                # on, and filtering by track name alone dropped the arrival day
                # from the skiers' copy.
                "members": [str(x) for x in (t.get("members") or [])],
                "alternative": bool(t.get("alternative")),
            })

    reserved = {}
    for slot in slots:
        want = slot.get("prefer")
        if not want:
            continue
        pick = next((o for o in options
                     if o["id"] not in reserved.values()
                     and (o["id"].lower() == want or want in o["title"].lower()
                          or want in o["theme"].lower())), None)
        if pick:
            reserved[id(slot)] = pick["id"]

    chosen, taken, prev_long = [], set(), False
    for slot in slots:
        idx, iso = slot["idx"], slot["iso"]
        want = slot["prefer"] or None
        if want:
            reserved_id = reserved.get(id(slot))
            pick = next((o for o in options if o["id"] == reserved_id), None)
            if pick:
                taken.add(pick["id"])
                prev_long = (pick["driving_round_trip_mins"] >= 240
                             or pick["stats"].get("day_length_hours", 0) >= 11)
                chosen.append((pick, slot))
                continue
        best, best_fit = None, None
        for o in shortlist:
            if o["id"] in taken or o["id"] in set(reserved.values()):
                continue
            f = day_fit(o, iso, windows, fixed_by_date, forecast, pace)
            if f is None:
                continue
            if prev_long and (o["driving_round_trip_mins"] >= 240
                              or o["stats"].get("day_length_hours", 0) >= 11):
                f -= 8.0                     # not two big days back to back
            if best_fit is None or f > best_fit:
                best, best_fit = o, f
        if best is None:
            best = next((o for o in shortlist if o["id"] not in taken), shortlist[0])
        taken.add(best["id"])
        prev_long = (best["driving_round_trip_mins"] >= 240
                     or best["stats"].get("day_length_hours", 0) >= 11)
        chosen.append((best, slot))

    # De-duplication can hollow out a day: an option that looked like five stops
    # re-emerges as two once earlier days have taken their share. The real
    # length is only knowable here, after re-scheduling, so the swap has to
    # happen here too - try an unused option rather than seat a 3-hour day.
    # De-duplication is per lineage, not global. Two groups that split up may
    # both want the gondola; the same person should not be sent up it twice.
    used_by_lineage, final = {}, []
    dining_by_date = {}
    picked_ids = {o["id"] for o, _ in chosen}
    for o, slot in chosen:
        lineages = slot["lineages"]
        used = set().union(*[used_by_lineage.setdefault(l, set()) for l in lineages])
        booked = dining_by_date.setdefault(slot["iso"], set())
        day = build_day(o, used | booked, slot["idx"], slot)
        if day["stats"].get("day_length_hours", 0) < 4.0:
            for alt in options:
                if alt["id"] in picked_ids:
                    continue
                cand = build_day(alt, used, slot["idx"], slot)
                if cand["stats"].get("day_length_hours", 0) > \
                        day["stats"].get("day_length_hours", 0) + 1.5:
                    picked_ids.discard(o["id"])
                    picked_ids.add(alt["id"])
                    day = cand
                    break
        booked |= {i["suggestion"] for i in day["timeline"]
                   if i["type"] == "meal" and i.get("suggestion")}
        fresh = {i["name"] for i in day["timeline"] if i["type"] == "stop"}
        for l in lineages:
            used_by_lineage[l] |= fresh
        day["lineages"] = lineages
        final.append(day)
    return final


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trip", required=True)
    ap.add_argument("--options-per-day", type=int, default=4)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    trip_dir = ROOT / "trips" / a.trip
    brief = json.loads((trip_dir / "brief.json").read_text())
    data = json.loads((trip_dir / "candidates.json").read_text())
    cands = data["candidates"]

    # Agent-supplied corrections: current prices, this season's closures,
    # web-search finds. The script does the arithmetic; the agent does the
    # judgement. Anything here wins over the harvested value.
    ov_path = trip_dir / "overrides.json"
    if ov_path.exists():
        ov = json.loads(ov_path.read_text())
        by_name = {c["name"].lower(): c for c in cands}
        for patch in ov.get("patch", []):
            tgt = by_name.get(patch.get("name", "").lower())
            if tgt:
                tgt.update({k: v for k, v in patch.items() if k != "name"})
                tgt["corrected_by_agent"] = True
                if "price" in patch or "hours" in patch:
                    tgt["stale"] = False
                    tgt["source_years_old"] = 0.0
        _g = geo.Geo(ROOT / "cache")
        for extra in ov.get("add", []):
            extra.setdefault("source", "agent-research")
            extra.setdefault("stale", False)
            extra.setdefault("kind", "do")
            extra.setdefault("duration_min", 120)
            if extra.get("themes_hint"):
                extra["themes_explicit"] = [t.strip() for t in
                                            extra["themes_hint"].split(",") if t.strip()]
            if extra.get("lat") is None:
                # A research entry that supplies geocode_as has already said
                # exactly where it means; do not second-guess it with a region.
                if extra.get("geocode_as"):
                    hit = _g.geocode(extra["geocode_as"], near="")
                else:
                    hit = _g.geocode(extra["name"],
                                     near=f"{data['destination']}, {data.get('region','')}")
                if hit:
                    extra["lat"], extra["lon"] = hit["lat"], hit["lon"]
                    extra["located_by"] = "geocoded from agent research"
                else:
                    extra["located_by"] = "UNLOCATED"
            else:
                extra.setdefault("located_by", "agent supplied")
            if extra.get("lat") is not None:
                extra["km_from_centre"] = round(geo.haversine_km(
                    (data["centre"]["lat"], data["centre"]["lon"]),
                    (extra["lat"], extra["lon"])), 1)
            cands.append(extra)
        _g.save()

        # Applied last, on purpose: an earlier version excluded before the
        # additions ran, so an override that re-added a name defeated the
        # exclusion without saying so - and The Remarkables took the ski slot
        # from Coronet Peak on a trip where only Coronet was wanted.
        drop = {n.lower() for n in ov.get("exclude", [])}
        if drop:
            before = len(cands)
            cands = [c for c in cands if c["name"].lower() not in drop]
            print(f"excluded {before - len(cands)} candidates by name")
        print(f"overrides: {len(ov.get('patch', []))} corrected, {len(ov.get('add', []))} added")

    start = dt.date.fromisoformat(brief["start_date"])
    n_days = int(brief["days"])
    dates = [start + dt.timedelta(days=i) for i in range(n_days)]
    month = start.month

    base = brief.get("base") or data["centre"]
    base_pt = (base["lat"], base["lon"])
    mode = {"car": "auto", "walk": "pedestrian", "bike": "bicycle",
            "public": "auto"}.get(brief.get("transport", "car"), "auto")
    pace = brief.get("pace", "moderate")

    g = geo.Geo(ROOT / "cache")

    # Anything already nailed down: landings, check-in, booked tours, the flight
    # home. These are placed at their stated times; the plan fits around them.
    fixed_by_date = {}
    for f in brief.get("fixed", []):
        entry = dict(f)
        entry["start"] = hhmm_to_min(f["start"])
        entry["end"] = hhmm_to_min(f["end"])
        if entry.get("lat") is None and entry.get("geocode_as"):
            hit = g.geocode(entry["geocode_as"], near="")
            if hit:
                entry["lat"], entry["lon"] = hit["lat"], hit["lon"]
        fixed_by_date.setdefault(f["date"], []).append(entry)

    windows = {d: (hhmm_to_min(v[0]), hhmm_to_min(v[1]))
               for d, v in (brief.get("day_windows") or {}).items()}

    forecast, (wx_src, wx_ok) = wx.forecast(
        base["lat"], base["lon"], start, start + dt.timedelta(days=n_days - 1),
        brief.get("timezone", "auto"), ROOT / "cache" / "weather.json")
    if wx_ok:
        print(f"weather: {len(forecast)} days of {wx_src}")
        for d, v in forecast.items():
            print(f"  {d}  [{v['band']}] {v['summary']}")
    else:
        print(f"weather: none ({wx_src})")

    for c in cands:
        c["themes"] = tag_themes(c)
        c["seasonal_risk"] = seasonal_risk(c, month)
        c["score"], c["why"] = score(c, brief)

    usable = [c for c in cands if c.get("lat") is not None and c["score"] > 0]
    usable.sort(key=lambda c: -c["score"])
    print(f"{len(cands)} candidates -> {len(usable)} usable after scoring")

    print("building day options ...")
    options, dining, by_name = build_options(usable, brief, base_pt, dates, g,
                                             mode, pace, a.options_per_day)
    print(f"  {len(options)} day options built, {len(dining)} places to eat held "
          f"back for meal slots")

    pool = usable
    for o in options:
        for item in o["timeline"]:
            if item["type"] == "stop":
                item["bench"] = bench_for(item, pool, g, mode)

    rec = recommend(options, n_days, brief, base_pt, g, mode, pace, dining,
                    by_name, dates, fixed_by_date, windows, forecast)
    for o in rec:
        for item in o["timeline"]:
            if item["type"] == "stop":
                item["bench"] = bench_for(item, pool, g, mode)

    g.save()

    out = {
        "trip": a.trip,
        "brief": brief,
        "destination": data["destination"],
        "region": data.get("region", ""),
        "base": base,
        "dates": [d.isoformat() for d in dates],
        "generated": dt.date.today().isoformat(),
        "day_trip_hubs": data.get("day_trip_hubs", []),
        "forecast": forecast,
        "forecast_source": wx_src,
        "options": options,
        "recommended": [o["id"] for o in rec],
        "plan": rec,
        "menu": [{"name": c["name"], "score": c["score"], "themes": c["themes"],
                  "why": c["why"], "kind": c["kind"], "price": c.get("price", ""),
                  "hours": c.get("hours", ""), "url": c.get("url", ""),
                  "image": c.get("image", ""), "desc": c.get("desc", "")[:300],
                  "km_from_centre": c.get("km_from_centre"),
                  "day_trip_hub": c.get("day_trip_hub", ""),
                  "stale": c.get("stale", True),
                  "source_years_old": c.get("source_years_old"),
                  "seasonal_risk": c.get("seasonal_risk", False),
                  "source": c.get("source", "")}
                 for c in usable[:80]],
    }

    if a.dry_run:
        for o in options[:12]:
            print(f"\n[{o['id']}] {o['title']}  score={o['score']}  "
                  f"{o['stats']['stops']} stops, {o['stats']['starts']}-{o['stats']['ends']}")
            for w in o["warnings"]:
                print(f"    ! {w}")
        return

    # Cost roll-up. Every priced item is parsed to an NZD range; anything with
    # no findable price is counted separately rather than treated as zero, so a
    # day total never quietly flatters itself.
    def cost_pass(day):
        entries = []
        for it in day["timeline"]:
            src = it.get("price") or it.get("suggestion_price") or ""
            # An explicit range wins over parsing. Some prices are additive -
            # a lift pass PLUS rental PLUS outerwear - and reading min/max out
            # of that sentence understates the day badly.
            explicit = it.get("price_nzd")
            if explicit and len(explicit) == 2:
                parsed = {"low": explicit[0], "high": explicit[1], "currency": "NZD",
                          "nzd_low": float(explicit[0]), "nzd_high": float(explicit[1]),
                          "confidence": "medium", "display": src or "stated"}
            else:
                parsed = money.parse(src, it.get("kind", ""))
            it["cost"] = parsed
            if it["type"] in ("stop", "fixed", "meal"):
                entries.append(parsed)
        lo, hi, counted, unpriced = money.nzd_range(entries)
        day["cost"] = {"nzd_low": lo, "nzd_high": hi, "priced": counted,
                       "unpriced": unpriced,
                       # "free" and "we could not find a price" are different
                       # claims, and printing the first for the second is a lie
                       # a traveller only discovers at the counter.
                       "display": money.fmt(lo, hi) if counted
                                  else "no prices found",
                       "per_person": True}
        return day

    for day in rec:
        cost_pass(day)
    for opt in options:
        cost_pass(opt)

    # Only the tracks you are actually on. Summing every track would bill one
    # person for two groups being in two places at once.
    # An alternative day is the same day done differently, not an extra day.
    # Billing someone for both halves of an either/or doubles their Tuesday.
    yours = [d for d in rec if d.get("primary", True) and not d.get("alternative")]
    trip_lo = sum(d["cost"]["nzd_low"] for d in yours)
    trip_hi = sum(d["cost"]["nzd_high"] for d in yours)
    trip_unpriced = sum(d["cost"]["unpriced"] for d in yours)
    out["cost_by_group"] = {}
    for d in rec:
        if d.get("alternative"):
            continue
        gk = d.get("group", "everyone")
        agg = out["cost_by_group"].setdefault(
            gk, {"label": d.get("group_label", gk), "size": d.get("group_size"),
                 "nzd_low": 0.0, "nzd_high": 0.0})
        agg["nzd_low"] += d["cost"]["nzd_low"]
        agg["nzd_high"] += d["cost"]["nzd_high"]
    for agg in out["cost_by_group"].values():
        agg["display"] = money.fmt(agg["nzd_low"], agg["nzd_high"])
    out["cost"] = {"nzd_low": round(trip_lo, 2), "nzd_high": round(trip_hi, 2),
                   "display": money.fmt(trip_lo, trip_hi),
                   "unpriced_items": trip_unpriced,
                   "basis": "per adult on YOUR track - activities and meals only, no "
                            "accommodation, fuel, or rental car",
                   "fx_note": f"Non-NZD prices converted at indicative rates "
                              f"({money.RATES_AS_OF})"}
    print(f"cost estimate: {out['cost']['display']} per adult "
          f"({trip_unpriced} items had no findable price)")

    # Where to eat, as a first-class list rather than something you only meet
    # inside a meal slot. The traveller's own picks lead it.
    seen_d = set()
    dining_list = []
    full_areas = set(brief.get("dining_full_areas") or ["Queenstown"])
    for c in sorted(dining, key=lambda c: (c.get("source") != "agent-research",
                                           -c.get("score", 0))):
        if c["name"] in seen_d:
            continue
        seen_d.add(c["name"])
        parsed = (money.parse(c.get("price", "")) if not c.get("price_nzd") else
                  {"nzd_low": float(c["price_nzd"][0]), "nzd_high": float(c["price_nzd"][1])})
        dining_list.append({
            "name": c["name"], "kind": c.get("kind", "eat"),
            "maps_query": c.get("maps_query", ""), "meal": c.get("meal", ""),
            "area": c.get("area") or area_for(c.get("lat"), c.get("lon")),
            "highlight_only": (c.get("area") or area_for(c.get("lat"), c.get("lon")))
                              not in full_areas,
            "price": c.get("price", ""), "cost": parsed,
            "url": c.get("url", ""), "desc": (c.get("desc") or "")[:220],
            "indoor": c.get("indoor", True), "lat": c.get("lat"), "lon": c.get("lon"),
            "yours": c.get("source") == "agent-research",
            "km_from_base": round(geo.haversine_km(base_pt, (c["lat"], c["lon"])), 1)
                            if c.get("lat") is not None else None,
        })
    out["dining"] = dining_list[:60]
    out["people"] = brief.get("people", [])
    out["ideas"] = brief.get("ideas", [])
    out["dining_full_areas"] = sorted(full_areas)
    out["transport_note"] = brief.get("transport_note", "")
    print(f"dining list: {len(out['dining'])} places "
          f"({sum(1 for x in out['dining'] if x['yours'])} from your own research)")

    out["packing"] = packing.build(out)
    print(f"packing list: {sum(len(s['items']) for s in out['packing'])} items across "
          f"{len(out['packing'])} sections")

    path = trip_dir / "plan.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"\nwrote {path}")
    print(f"recommended mix: {', '.join(o['title'] for o in rec)}")


if __name__ == "__main__":
    main()
