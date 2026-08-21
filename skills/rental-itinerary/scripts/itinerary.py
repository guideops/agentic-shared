#!/usr/bin/env python3
"""Build a property-viewing itinerary from the operator's 'Apartments' tab.

Reads the hand-curated shortlist, geocodes each property, works out the real
walk from its nearest station, clusters properties that are worth seeing in one
trip, and orders everything High -> Medium -> Low priority, minimising travel
inside each priority tier.

Deliberately produces NO clock times. Inspection slots are set by agents, not by
us; what this gives you is the order to see things in and how long each hop
takes, so you can drop real times into it as they get booked.

Usage:
  python3 itinerary.py [--per-day N] [--tab "Viewing Plan"] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

BASE_DIR = pathlib.Path("/root/agentic-workspace/automations/sydney-rentals")
sys.path.insert(0, str(BASE_DIR))
import sheets      # noqa: E402
import walking     # noqa: E402

CONFIG = json.loads((BASE_DIR / "config.json").read_text())
KEY = BASE_DIR / "service-account.json"
STATIONS = json.loads((BASE_DIR / "stations.json").read_text())
WALK = walking.WalkCache(BASE_DIR / "walk-cache.json")
GEO_CACHE = pathlib.Path(__file__).parent.parent / "geocode-cache.json"
PLAN_JSON = pathlib.Path(__file__).parent.parent / "plan.json"


def listing_id(url: str) -> str:
    """The trailing numeric id in a listing url - the key everything joins on."""
    m = re.search(r"-(\d{6,})(?:[?#]|$)", (url or "").split("?")[0])
    return m.group(1) if m else ""

UA = {"User-Agent": "sydney-rentals-itinerary/1.0 (personal rental search)"}
STREET_WORDS = {
    "street", "st", "road", "rd", "avenue", "ave", "drive", "dr", "place", "pl",
    "parade", "pde", "crescent", "cr", "cres", "lane", "ln", "court", "ct",
    "terrace", "tce", "circuit", "cct", "boulevard", "bvd", "highway", "hwy",
    "close", "grove", "walk", "esplanade", "quay", "way", "row", "square",
}
STATES = {"nsw", "vic", "qld", "wa", "sa", "tas", "act", "nt"}
RAIL_KMH = 35.0          # Sydney rail average including stops
CHANGE_PENALTY_MIN = 6   # a different line usually costs an interchange
CLUSTER_KM = 2.5
MAX_MIDDAY_HOP_MIN = 25   # further than this and it becomes another day


# --------------------------------------------------------------------------
# address extraction + geocoding
# --------------------------------------------------------------------------
def address_from_url(url: str):
    """Pull a street address out of a domain.com.au listing slug.

    'https://…/1112-23-halifax-street-macquarie-park-nsw-2113-18250473'
      -> '23 Halifax Street, Macquarie Park NSW 2113'
    Returns None when the url carries no address (realestate.com.au does not).
    """
    if "domain.com.au" not in url:
        return None
    slug = urllib.parse.urlparse(url).path.strip("/").split("/")[-1]
    parts = [p for p in slug.split("-") if p]
    if parts and parts[-1].isdigit() and len(parts[-1]) >= 6:
        parts.pop()                                   # listing id
    postcode = parts.pop() if parts and re.fullmatch(r"\d{4}", parts[-1]) else ""
    if parts and parts[-1].lower() in STATES:
        parts.pop()
    if not parts:
        return None

    idx = max((i for i, w in enumerate(parts) if w.lower() in STREET_WORDS),
              default=None)
    if idx is None:
        return None
    street_parts, suburb_parts = parts[:idx + 1], parts[idx + 1:]

    # Strip a leading UNIT token but never the street number. '1112-23-halifax-
    # street' is unit 1112 at 23 Halifax Street: drop the unit only when a
    # numeric street number follows it, or the address loses its number.
    if len(street_parts) >= 3 and street_parts[0].isdigit() \
            and street_parts[1].lower() == "bedroom":
        street_parts = street_parts[2:]                      # '1-bedroom-5-…'
    elif len(street_parts) >= 3 \
            and re.fullmatch(r"(level\d+|[a-z]{0,3}\d{1,5}[a-z]?)",
                             street_parts[0], re.I) \
            and street_parts[1].isdigit():
        street_parts = street_parts[1:]

    # rejoin a street-number range: ['7','9','gertrude','street'] -> '7-9 …'
    if len(street_parts) >= 3 and street_parts[0].isdigit() \
            and street_parts[1].isdigit():
        street_parts = [f"{street_parts[0]}-{street_parts[1]}"] + street_parts[2:]

    street = " ".join(street_parts).title()
    suburb = " ".join(suburb_parts).title()
    if not suburb:
        return None
    return f"{street}, {suburb} NSW {postcode}".strip()


PRIORITY_ALIASES = {"middle": "Medium", "med": "Medium", "mid": "Medium",
                    "hi": "High", "urgent": "High"}


def norm_priority(value):
    """The operator types these by hand - 'Middle', 'low' and 'Medium' all
    appear on the tab. Map them onto the three real tiers rather than silently
    sorting an unrecognised word to the bottom."""
    v = (value or "").strip().lower()
    if not v:
        return "Low"
    return PRIORITY_ALIASES.get(v, v.title())


def geocode(query: str, cache: dict, suburb: bool = False):
    """Geocode an address, or a suburb when `suburb` is set.

    Suburb lookups MUST use Nominatim's structured form. Free text resolves
    'Macquarie Park NSW' to 'Macquarie Place Park' in the CBD - 13 km wrong -
    and 'Rhodes NSW' to a parcel locker. The structured query returns the
    actual suburb every time.
    """
    key = ("suburb:" if suburb else "") + query
    if key in cache:
        c = cache[key]
        return (c["lat"], c["lon"]) if c else None
    time.sleep(1.1)                                   # Nominatim asks for <=1 req/s
    params = ({"city": query, "state": "New South Wales", "country": "Australia"}
              if suburb else {"q": f"{query}, Australia"})
    params.update({"format": "json", "limit": 1, "countrycodes": "au"})
    u = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    try:
        r = json.load(urllib.request.urlopen(
            urllib.request.Request(u, headers=UA), timeout=30))
    except Exception as exc:
        print(f"[warn] geocode failed for {query}: {exc}", file=sys.stderr)
        return None
    if not r:
        cache[key] = None
        return None
    hit = (float(r[0]["lat"]), float(r[0]["lon"]))
    cache[key] = {"lat": hit[0], "lon": hit[1]}
    return hit


# --------------------------------------------------------------------------
# travel model
# --------------------------------------------------------------------------
def travel(a: dict, b: dict):
    """(minutes, description) between two located stops, on foot or by rail."""
    door_km = walking.haversine_m(a["lat"], a["lon"], b["lat"], b["lon"]) / 1000
    if door_km < 1.2:
        mins, _ = WALK.minutes((a["lat"], a["lon"]), (b["lat"], b["lon"]))
        return round(mins), "walk"

    a_st, a_walk = a.get("station"), a.get("station_walk") or 0
    b_st, b_walk = b.get("station"), b.get("station_walk") or 0
    if not a_st or not b_st:
        return round(door_km / RAIL_KMH * 60 + 10), "transit (approx)"

    rail_km = walking.haversine_m(a_st["lat"], a_st["lon"],
                                  b_st["lat"], b_st["lon"]) / 1000
    mins = a_walk + rail_km / RAIL_KMH * 60 + b_walk
    if a_st.get("kind") != b_st.get("kind"):
        mins += CHANGE_PENALTY_MIN
    return round(mins), f"{a_st['name']} → {b_st['name']}"


def cluster(stops):
    """Single-linkage grouping: stops within CLUSTER_KM chain into one trip."""
    groups = []
    for s in stops:
        joined = None
        for g in groups:
            if any(walking.haversine_m(s["lat"], s["lon"], m["lat"], m["lon"])
                   / 1000 <= CLUSTER_KM for m in g):
                if joined is None:
                    g.append(s)
                    joined = g
                else:                                  # bridges two groups
                    joined.extend(g)
                    g.clear()
        if joined is None:
            groups.append([s])
    return [g for g in groups if g]


def walk_verdict(stop):
    """How this property scores against the operator's station-walk rule:
    under 8 min preferred, up to 10 tolerated, over 10 is out."""
    m = stop["station_walk"]
    if stop["located_by"].startswith("SUBURB"):
        return f"~{m:.0f} min (suburb estimate - verify)"
    if m > CONFIG["max_station_walk_mins"]:
        return f"OVER - {m:.1f} min"
    if m > CONFIG["prefer_station_walk_mins"]:
        return f"tolerated - {m:.1f} min"
    return f"good - {m:.1f} min"


def order_cluster(origin, group, rank):
    """Order one cluster: higher priority first, travel only breaking ties.

    Without this the nearest-neighbour walk can put a Low before a Medium in
    the same suburb, which is backwards - you want to see the one you care
    about while you still have energy.
    """
    out, cur = [], origin
    for r in sorted({rank(s) for s in group}):
        sub = order_from(cur, [s for s in group if rank(s) == r])
        out.extend(sub)
        cur = sub[-1]
    return out


def order_from(origin, items, keyfn=lambda x: x):
    """Greedy nearest-neighbour ordering starting at `origin`."""
    remaining, out, cur = list(items), [], origin
    while remaining:
        nxt = min(remaining, key=lambda x: travel(cur, keyfn(x))[0])
        out.append(nxt)
        cur = keyfn(nxt)
        remaining.remove(nxt)
    return out


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-day", type=int, default=4,
                    help="viewings per day; keeps the trip humane")
    ap.add_argument("--tab", default="Viewing Plan")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pdf", nargs="?", const="", default=None, metavar="PATH",
                    help="also render the illustrated PDF itinerary")
    ap.add_argument("--fetch-photos", action="store_true",
                    help="download listing photos while building the PDF; only "
                         "works from a machine Domain's CDN will serve (laptop)")
    args = ap.parse_args()

    src_gid = (CONFIG.get("exclude_tab_gids") or [None])[0]
    rows = sheets.read_table(CONFIG["spreadsheet_id"], KEY, src_gid)
    print(f"[info] {len(rows)} rows on the source tab", file=sys.stderr)

    cache = json.loads(GEO_CACHE.read_text()) if GEO_CACHE.exists() else {}
    stops, unlocated = [], []
    skipped_dead = 0
    for i, r in enumerate(rows):
        # the watcher writes bot_status into this tab; do not plan a trip to a
        # property that is already leased
        bs = str(r.get("bot_status") or "")
        if bs.startswith("OFF MARKET") or bs.startswith("gone"):
            skipped_dead += 1
            continue
        link = (r.get("Link") or "").strip()
        loc = (r.get("Location") or "").strip()
        addr = address_from_url(link)
        pt = geocode(addr, cache) if addr else None
        how = "address"
        if pt is None and loc:
            pt = geocode(loc, cache, suburb=True)
            how = "SUBURB ONLY - no street address in link"
            addr = addr or loc
        if pt is None:
            unlocated.append(loc or link)
            continue
        st, walk_min, _ = walking.best_walk(pt, STATIONS, WALK, limit=4)
        stops.append({
            "row": i + 2, "link": link, "address": addr, "suburb": loc,
            "cost": (r.get("Cost") or "").strip(),
            "comments": (r.get("Comments") or "").strip(),
            "priority": norm_priority(r.get("Priority")),
            "lat": pt[0], "lon": pt[1], "located_by": how,
            "station": st, "station_walk": walk_min,
        })
    GEO_CACHE.write_text(json.dumps(cache, indent=1))
    WALK.save()
    if skipped_dead:
        print(f"[info] skipped {skipped_dead} already off the market", file=sys.stderr)
    if unlocated:
        print(f"[warn] could not locate: {unlocated}", file=sys.stderr)

    base = {"name": CONFIG["base"]["name"], "lat": CONFIG["base"]["lat"],
            "lon": CONFIG["base"]["lon"], "station": None, "station_walk": 0}
    b_st, b_walk, _ = walking.best_walk((base["lat"], base["lon"]), STATIONS, WALK)
    base["station"], base["station_walk"] = b_st, b_walk

    # Priority decides WHICH AREA you go to next. Geography decides what you do
    # once you are there: a Low sitting in the same suburb as a Medium is worth
    # seeing on the same trip rather than earning its own trip across the city.
    RANK = {"High": 0, "Medium": 1, "Low": 2}
    rank = lambda s: RANK.get(s["priority"], 3)

    groups = cluster(stops)
    for g in groups:
        g.sort(key=rank)
    # a cluster is worth as much as the best property in it
    groups.sort(key=lambda g: min(rank(s) for s in g))

    # visit clusters best-tier-first, nearest-first inside a tier
    ordered, cur = [], base
    for tier in sorted({min(rank(s) for s in g) for g in groups}):
        tier_groups = [g for g in groups if min(rank(s) for s in g) == tier]
        for g in order_from(cur, tier_groups, keyfn=lambda grp: grp[0]):
            ordered.append(g)
            cur = g[-1]

    plan, day, slot, cur = [], 1, 0, base
    for gi, g in enumerate(ordered):
        g = order_cluster(cur if slot else base, g, rank)
        for stop in g:
            hop, via = travel(cur if slot else base, stop)
            # New day when the day is full, or when this stop is a long hop from
            # what we just saw - crossing the city mid-day is how a trip burns you out.
            if slot >= args.per_day or (slot and hop > MAX_MIDDAY_HOP_MIN):
                day, slot, cur = day + 1, 0, base
                hop, via = travel(base, stop)
            # Two suburb-only points share a centroid, so "0 min" would be a
            # fiction. Say what we actually know instead.
            if (stop["located_by"].startswith("SUBURB")
                    and str(cur.get("located_by", "")).startswith("SUBURB")
                    and cur.get("suburb") == stop["suburb"]):
                via = "same suburb - exact address unknown"
            slot += 1
            best_tier = min(rank(x) for x in g)
            plan.append({
                "day": f"Day {day}", "stop": slot, "priority": stop["priority"],
                "suburb": stop["suburb"], "address": stop["address"],
                "cost_pw": stop["cost"],
                "from": cur.get("name") or cur.get("address") or "base",
                "travel_via": via, "travel_mins": hop,
                "station": (stop["station"] or {}).get("name", ""),
                "walk_from_station_mins": round(stop["station_walk"], 1),
                "why_now": ("priority" if rank(stop) == best_tier
                            else "already in the area"),
                "walk_rule": walk_verdict(stop),
                "located_by": stop["located_by"],
                "your_comments": stop["comments"], "link": stop["link"],
                "lat": stop["lat"], "lon": stop["lon"],
                "listing_id": listing_id(stop["link"]),
                "station_lat": (stop["station"] or {}).get("lat"),
                "station_lon": (stop["station"] or {}).get("lon"),
            })
            cur = stop

    cols = ["day", "stop", "priority", "why_now", "suburb", "address", "cost_pw",
            "from", "travel_via", "travel_mins", "station",
            "walk_from_station_mins", "walk_rule", "located_by",
            "your_comments", "link"]
    for p in plan:
        print(f"  {p['day']:>6} #{p['stop']}  {p['priority']:<6} {p['suburb'][:15]:<15} "
              f"{p['travel_mins']:>3}min {p['travel_via'][:32]:<32} "
              f"walk {p['walk_from_station_mins']:>4}  {p['why_now']}", file=sys.stderr)

    if args.dry_run:
        print(f"[dry-run] {len(plan)} stops over {plan[-1]['day'] if plan else '-'}",
              file=sys.stderr)
        return 0

    # Sidecar for the PDF renderer: coordinates and listing ids that the flat
    # sheet has no column for. The sheet stays the thing you correct data in;
    # this is only ever derived from it.
    # Carry the photo URLs into the plan itself. They cost nothing (they ride in
    # the Apify payload the watcher already pays for) and baking them in here is
    # what lets the PDF be rendered on a laptop that has no state.json, no
    # service-account key, and no copy of the watcher at all.
    try:
        st = json.loads((BASE_DIR / "state.json").read_text())
    except Exception:
        st = {}
    for row in plan:
        row["images"] = (st.get(row.get("listing_id") or "") or {}).get("images") or []

    PLAN_JSON.write_text(json.dumps(
        {"base": {k: base[k] for k in ("name", "lat", "lon")},
         "trip": CONFIG.get("trip", {}), "stops": plan}, indent=1))

    gid = sheets.ensure_tab(CONFIG["spreadsheet_id"], KEY, args.tab)
    rows_out = [{c: p.get(c, "") for c in cols} for p in plan]
    sheets.replace(CONFIG["spreadsheet_id"], KEY, cols, rows_out, gid,
                   signature={"day", "stop", "link"})
    print(f"[info] wrote {len(plan)} stops to '{args.tab}'", file=sys.stderr)

    if args.pdf is not None:
        import pdf as pdfmod
        out = pdfmod.build(PLAN_JSON, args.pdf or None,
                           fetch_photos=args.fetch_photos)
        print(f"[info] pdf: {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
