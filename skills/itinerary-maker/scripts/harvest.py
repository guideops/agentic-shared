#!/usr/bin/env python3
"""Phase 1+2: harvest and enrich candidate activities for a destination.

Three free, keyless sources, in descending order of trust:

  Wikivoyage   the spine. Human-curated listing templates carrying name,
               coordinates, hours, price, phone, url and a description - plus
               `lastedit`, which is the only honest staleness signal any of
               these sources gives us.
  Wikipedia    a summary paragraph and a Commons image for the marquee items.
  Overpass     coordinates and gap-filling only. Excellent at 'where is this',
               useless at 'is this worth doing' - its unfiltered top results
               for a resort town include derelict huts and unnamed viewpoints.

What this script deliberately does NOT do is judge. It gathers, structures and
flags; the agent adds web-search candidates and the scoring happens in plan.py.

Usage:
  harvest.py --dest "Queenstown" --region "New Zealand" [--trip SLUG]
             [--radius-km 25] [--no-overpass]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import geo  # noqa: E402

UA = {"User-Agent": "itinerary-maker/1.0 (personal trip planning; operator contact via hello@guidantoperations.tech)"}
WV_API = "https://en.wikivoyage.org/w/api.php"
WP_API = "https://en.wikipedia.org/w/api.php"
WP_REST = "https://en.wikipedia.org/api/rest_v1/page/summary/"

# How old a Wikivoyage listing may be before its price and hours stop counting
# as information and start counting as folklore.
STALE_YEARS = 2

# Rough time-on-site by listing kind, in minutes. Overridden by anything the
# source actually states; these only stop the scheduler from assuming zero.
DEFAULT_DURATION = {
    "see": 60, "do": 120, "eat": 75, "drink": 75, "buy": 45,
    "viewpoint": 30, "museum": 90, "attraction": 60,
}

# Keywords that mark a listing as ruined by bad weather. An itinerary that
# cannot tell an indoor museum from an alpine hike has no Plan B to offer.
OUTDOOR_WORDS = re.compile(
    r"\b(hike|hiking|walk|walking|track|trail|summit|peak|alpine|lake|beach|"
    r"cruise|kayak|raft|rafting|jet ?boat|bungy|skydiv|paraglid|zipline|bike|"
    r"cycl|ski|snowboard|garden|park|viewpoint|lookout|scenic|glacier|"
    r"vineyard|golf|fish|sail|canyon|climb|horse)\b", re.I)
INDOOR_WORDS = re.compile(
    r"\b(museum|gallery|cinema|theatre|theater|spa|brewery|distiller|"
    r"restaurant|cafe|café|bar|aquarium|indoor|arcade|casino|library)\b", re.I)


_last_wm = [0.0]
WM_GAP_S = 1.2          # Wikimedia rate-limits an unthrottled client hard


def _wm_throttle():
    import time
    wait = WM_GAP_S - (time.time() - _last_wm[0])
    if wait > 0:
        time.sleep(wait)
    _last_wm[0] = time.time()


def wm_open(url: str, timeout: int = 25, tries: int = 4):
    """GET a Wikimedia URL, throttled, with exponential backoff on 429.

    Learned the hard way: sixty unthrottled calls in a row earns a 429 and the
    run dies two thirds of the way through a harvest.
    """
    import time
    delay = 2.0
    for attempt in range(tries):
        _wm_throttle()
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
    raise RuntimeError("unreachable")


def api_get(base: str, params: dict, timeout: int = 25):
    params = dict(params, format="json", formatversion=2)
    url = base + "?" + urllib.parse.urlencode(params)
    return json.loads(wm_open(url, timeout))


# --------------------------------------------------------------------------
# Wikivoyage
# --------------------------------------------------------------------------
def resolve_page(dest: str, region: str) -> str | None:
    """Find the Wikivoyage page for a destination.

    Tries the disambiguated form first - 'Queenstown' alone is a town in
    Tasmania, Singapore and South Africa as well as New Zealand.
    """
    for query in (f"{dest} ({region})", f"{dest} {region}", dest):
        try:
            d = api_get(WV_API, {"action": "query", "list": "search",
                                 "srsearch": query, "srlimit": 5})
        except Exception:
            continue
        for hit in d.get("query", {}).get("search", []):
            title = hit["title"]
            if dest.lower() in title.lower():
                return title
    return None


def split_templates(wikitext: str):
    """Yield (template_name, body) for every top-level {{...}} in the text.

    Written as a brace scanner rather than a regex because listing bodies
    contain nested templates ({{flag}}, {{km}}) that a lazy regex swallows.
    """
    i = 0
    n = len(wikitext)
    while i < n - 1:
        if wikitext[i] == "{" and wikitext[i + 1] == "{":
            depth = 0
            j = i
            while j < n - 1:
                if wikitext[j:j + 2] == "{{":
                    depth += 1
                    j += 2
                elif wikitext[j:j + 2] == "}}":
                    depth -= 1
                    j += 2
                    if depth == 0:
                        break
                else:
                    j += 1
            body = wikitext[i + 2:j - 2]
            name = body.split("|", 1)[0].strip().lower()
            yield name, body
            i = j
        else:
            i += 1


def parse_fields(body: str) -> dict:
    """Split a listing body into its named fields, respecting nesting."""
    fields, depth, buf = {}, 0, []
    parts = []
    for ch in body:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if ch == "|" and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    for p in parts[1:]:
        if "=" not in p:
            continue
        k, v = p.split("=", 1)
        fields[k.strip().lower()] = clean(v)
    return fields


def clean(s: str) -> str:
    """Wikitext -> readable plain text."""
    s = s.replace("&nbsp;", " ")
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)      # piped links
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)                 # plain links
    s = re.sub(r"\[(?:https?|ftp)://\S+\s+([^\]]+)\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)                      # leftover templates
    s = re.sub(r"'''?", "", s)                                # bold/italic
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", s).strip()


def staleness(lastedit: str):
    """(years_old, is_stale). Missing dates count as stale, not as fresh."""
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", lastedit or "")
    if not m:
        return None, True
    then = dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    years = round((dt.date.today() - then).days / 365.25, 1)
    return years, years > STALE_YEARS


def weather_profile(name: str, desc: str, kind: str):
    """(indoor, weather_sensitive) from the words the source used."""
    text = f"{name} {desc}"
    indoor = bool(INDOOR_WORDS.search(text))
    outdoor = bool(OUTDOOR_WORDS.search(text))
    if indoor and not outdoor:
        return True, False
    if outdoor:
        return False, True
    return (kind in ("eat", "drink", "buy")), False


def from_wikivoyage(title: str) -> list[dict]:
    d = api_get(WV_API, {"action": "parse", "page": title, "prop": "wikitext"})
    wikitext = d["parse"]["wikitext"]
    out = []
    for tname, body in split_templates(wikitext):
        kind = tname
        if tname == "listing":
            f = parse_fields(body)
            kind = (f.get("type") or "see").lower()
        elif tname not in ("see", "do", "eat", "drink", "buy"):
            continue
        f = parse_fields(body)
        name = f.get("name", "")
        if not name:
            continue
        desc = f.get("content", "")
        years, stale = staleness(f.get("lastedit", ""))
        lat, lon = f.get("lat", ""), f.get("long", "")
        indoor, wx = weather_profile(name, desc, kind)
        out.append({
            "name": name,
            "kind": kind,
            "desc": desc,
            "lat": float(lat) if _num(lat) else None,
            "lon": float(lon) if _num(lon) else None,
            "address": f.get("address", ""),
            "directions": f.get("directions", ""),
            "hours": f.get("hours", ""),
            "price": f.get("price", ""),
            "phone": f.get("phone", "") or f.get("tollfree", ""),
            "url": f.get("url", ""),
            "duration_min": DEFAULT_DURATION.get(kind, 60),
            "indoor": indoor,
            "weather_sensitive": wx,
            "source": "wikivoyage",
            "source_years_old": years,
            "stale": stale,
            "image": "",
        })
    return out


def _num(s) -> bool:
    try:
        float(s)
        return True
    except Exception:
        return False



def district_pages(wikitext: str, title: str) -> list[str]:
    """Wikivoyage subpages of a big city, e.g. 'Lisbon/Alfama'.

    Large cities put their overview on the main article and their actual
    listings on district subpages. Harvesting only the top page produced a
    Lisbon plan whose best ideas were a fashion week and a tourist information
    desk, with no Jeronimos, no Alfama and no Belem anywhere in it.
    """
    import re as _re
    base = title.split("(")[0].strip()
    found = _re.findall(r"\[\[(" + _re.escape(base) + r"/[^\]|#]+)", wikitext)
    seen, out = set(), []
    for f in found:
        f = f.strip()
        if f.lower() not in seen:
            seen.add(f.lower())
            out.append(f)
    return out


def harvest_district(page: str) -> list[dict]:
    """Listings from one district subpage, tagged with the district name."""
    try:
        listings = from_wikivoyage(page)
    except Exception:
        return []
    district = page.split("/", 1)[1] if "/" in page else page
    for c in listings:
        c["district"] = district
    return listings


# --------------------------------------------------------------------------
# neighbouring destinations
# --------------------------------------------------------------------------
def go_next(wikitext: str) -> list[str]:
    """Destinations the Wikivoyage page itself points you at.

    A base town's own listings stop at its outskirts, so harvesting only those
    produced a Queenstown plan with no Milford Sound, no Glenorchy and no
    Arrowtown in it - which is not a Queenstown plan. 'Go next' and 'Nearby'
    are where the region actually lives.
    """
    import re as _re
    names, seen = [], set()
    for heading in ("Go next", "Nearby", "Day trips", "Around"):
        m = _re.search(rf"==+\s*{heading}\s*==+(.*?)(?=\n==[^=]|\Z)",
                       wikitext, _re.S | _re.I)
        if not m:
            continue
        for link in _re.findall(r"\[\[([^\]|#]+)", m.group(1)):
            name = link.strip()
            # Skip cross-wiki, category and template links, and anything that
            # is a whole country or region rather than somewhere you can drive.
            if ":" in name or not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            names.append(name)
    return names


def harvest_hub(name: str, region: str, centre, g, max_listings: int = 12):
    """Harvest one neighbouring destination as a set of day-trip candidates.

    Returns (candidates, hub_info). Everything comes back tagged with the hub
    it belongs to and the drive from base, because a day trip is scheduled as
    a whole day, not as an ordinary stop.
    """
    title = resolve_page(name, region)
    if not title:
        return [], None
    try:
        listings = from_wikivoyage(title)
    except Exception:
        return [], None

    hub_pt = g.geocode(name, near=region)
    if not hub_pt:
        return [], None
    drive = g.route((centre["lat"], centre["lon"]), (hub_pt["lat"], hub_pt["lon"]), "auto")

    # Rank by how much the source had to say - a listing with a real
    # description is a real attraction; a bare name is usually filler.
    listings.sort(key=lambda c: -len(c.get("desc", "")))
    out = []
    for c in listings[:max_listings]:
        if c["lat"] is None:
            c["lat"], c["lon"] = hub_pt["lat"], hub_pt["lon"]
            c["located_by"] = "hub centre (approximate)"
        else:
            c["located_by"] = "source coordinates"
        c["day_trip_hub"] = name
        c["hub_drive_mins"] = drive["mins"] if drive else None
        c["hub_drive_km"] = drive["km"] if drive else None
        c["hub_drive_how"] = drive["how"] if drive else "unknown"
        out.append(c)

    hub = {"name": name, "page": title, "lat": hub_pt["lat"], "lon": hub_pt["lon"],
           "drive_mins": drive["mins"] if drive else None,
           "drive_km": drive["km"] if drive else None,
           "drive_how": drive["how"] if drive else "unknown",
           "round_trip_mins": round(drive["mins"] * 2) if drive else None,
           "listings": len(out)}
    return out, hub

# --------------------------------------------------------------------------
# Wikipedia images
# --------------------------------------------------------------------------
def wikipedia_image(name: str, region: str):
    """(image_url, extract) for a place, or ('','')."""
    try:
        d = api_get(WP_API, {"action": "query", "list": "search",
                             "srsearch": f"{name} {region}", "srlimit": 1})
        hits = d.get("query", {}).get("search", [])
        if not hits:
            return "", ""
        title = hits[0]["title"]
        s = json.loads(wm_open(
            WP_REST + urllib.parse.quote(title.replace(" ", "_")), timeout=20))
        # Wikimedia serves pre-rendered thumbnail sizes only, and which sizes
        # exist varies per image - rewriting every URL to a fixed 1024px width
        # earned a 400 on almost all of them. Take the size the API offers.
        img = (s.get("thumbnail") or {}).get("source", "")
        if not img:
            img = (s.get("originalimage") or {}).get("source", "")
        return img, s.get("extract", "")
    except Exception:
        return "", ""


# --------------------------------------------------------------------------
# merge
# --------------------------------------------------------------------------
def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def merge(primary: list[dict], extra: list[dict]) -> list[dict]:
    """Add `extra` to `primary`, skipping anything already there.

    Matched on normalised name, or on being within 200 m of an existing entry
    with an overlapping name token - 'Skyline Queenstown' and 'Skyline Gondola'
    are one attraction, not two.
    """
    seen = {norm(c["name"]): c for c in primary}
    out = list(primary)
    for c in extra:
        k = norm(c["name"])
        if k in seen:
            continue
        dup = False
        if c.get("lat") is not None:
            for p in primary:
                if p.get("lat") is None:
                    continue
                if geo.haversine_km((c["lat"], c["lon"]), (p["lat"], p["lon"])) < 0.2:
                    toks_a = set(c["name"].lower().split())
                    toks_b = set(p["name"].lower().split())
                    if toks_a & toks_b:
                        dup = True
                        break
        if not dup:
            out.append(c)
            seen[k] = c
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True)
    ap.add_argument("--region", default="")
    ap.add_argument("--trip", default="")
    ap.add_argument("--radius-km", type=float, default=25.0)
    ap.add_argument("--no-overpass", action="store_true")
    ap.add_argument("--districts", type=int, default=8,
                    help="harvest up to N Wikivoyage district subpages "
                         "(big cities keep their listings there, not on the "
                         "main article). 0 disables.")
    ap.add_argument("--day-trips", default="",
                    help="comma-separated neighbouring destinations to harvest too")
    ap.add_argument("--auto-day-trips", type=int, default=0,
                    help="also harvest the first N destinations Wikivoyage's "
                         "'Go next' section links to")
    ap.add_argument("--max-drive-mins", type=float, default=300.0,
                    help="drop a day trip further than this from base")
    ap.add_argument("--images", type=int, default=25,
                    help="fetch Wikipedia images for the top N by description length")
    a = ap.parse_args()

    slug = a.trip or re.sub(r"[^a-z0-9]+", "-", a.dest.lower()).strip("-")
    trip_dir = ROOT / "trips" / slug
    trip_dir.mkdir(parents=True, exist_ok=True)
    g = geo.Geo(ROOT / "cache")

    print(f"[1/5] resolving '{a.dest}' on Wikivoyage ...")
    title = resolve_page(a.dest, a.region)
    if not title:
        print(f"  ! no Wikivoyage page found for {a.dest}. "
              f"Harvest will rely on Overpass and agent web search only.")
        cands = []
        _wt = ""
    else:
        print(f"  page: {title}")
        cands = from_wikivoyage(title)
        _wt = api_get(WV_API, {"action": "parse", "page": title,
                               "prop": "wikitext"})["parse"]["wikitext"]
        print(f"  {len(cands)} listings parsed")

    print("[2/5] locating the destination centre ...")
    centre = g.geocode(a.dest, near=a.region)
    if not centre:
        sys.exit(f"could not geocode '{a.dest}, {a.region}' - check the spelling")
    print(f"  {centre['lat']:.4f}, {centre['lon']:.4f}")

    print("[3/5] geocoding listings that carry no coordinates ...")
    missing = [c for c in cands if c["lat"] is None]
    for c in missing:
        hit = g.geocode(c["name"], near=f"{a.dest}, {a.region}")
        if hit:
            c["lat"], c["lon"] = hit["lat"], hit["lon"]
            c["located_by"] = "geocoded"
        else:
            c["located_by"] = "UNLOCATED"
    for c in cands:
        c.setdefault("located_by", "source coordinates")
    print(f"  {len(missing)} needed lookup, "
          f"{sum(1 for c in cands if c['located_by'] == 'UNLOCATED')} still unlocated")

    if a.districts and _wt:
        subs = district_pages(_wt, title)[:a.districts]
        if subs:
            print(f"[3a] {len(subs)} district subpages ...")
            for sub in subs:
                extra = harvest_district(sub)
                for c in extra:
                    if c["lat"] is None:
                        hit = g.geocode(c["name"], near=f"{a.dest}, {a.region}")
                        if hit:
                            c["lat"], c["lon"] = hit["lat"], hit["lon"]
                            c["located_by"] = "geocoded"
                        else:
                            c["located_by"] = "UNLOCATED"
                    else:
                        c["located_by"] = "source coordinates"
                before = len(cands)
                cands = merge(cands, extra)
                print(f"  + {sub}: {len(extra)} listings, {len(cands) - before} new")

    hubs = []
    wanted = [x.strip() for x in a.day_trips.split(",") if x.strip()]
    if a.auto_day_trips:
        suggested = [n for n in go_next(_wt) if n.lower() not in
                     {w.lower() for w in wanted}]
        wanted += suggested[:a.auto_day_trips]
    if wanted:
        print(f"[3b] harvesting {len(wanted)} neighbouring destinations ...")
        for name in wanted:
            extra, hub = harvest_hub(name, a.region, centre, g)
            if not hub:
                print(f"  - {name}: no Wikivoyage page, skipped")
                continue
            if hub["drive_mins"] and hub["drive_mins"] > a.max_drive_mins:
                print(f"  - {name}: {hub['drive_mins']:.0f} min each way, "
                      f"beyond --max-drive-mins, skipped")
                continue
            before = len(cands)
            cands = merge(cands, extra)
            hubs.append(hub)
            print(f"  + {name}: {hub['drive_mins']:.0f} min / "
                  f"{hub['drive_km']:.0f} km each way, "
                  f"{len(cands) - before} new listings")

    if not a.no_overpass:
        print("[4/5] Overpass gap-fill ...")
        found = geo.pois_near(
            centre["lat"], centre["lon"], int(a.radius_km * 1000),
            {"tourism": "attraction|viewpoint|museum|gallery|zoo|theme_park",
             "leisure": "nature_reserve|park|garden",
             "natural": "peak|waterfall|hot_spring"},
            limit=80)
        extra = []
        for p in found:
            indoor, wx = weather_profile(p["name"], "", p["osm_kind"])
            extra.append({
                "name": p["name"], "kind": "see", "desc": "",
                "lat": p["lat"], "lon": p["lon"], "address": "",
                "directions": "", "hours": p["opening_hours"], "price": "",
                "phone": p["phone"], "url": p["website"],
                "duration_min": DEFAULT_DURATION.get(p["osm_kind"], 45),
                "indoor": indoor, "weather_sensitive": wx,
                "source": "overpass", "source_years_old": None, "stale": True,
                "located_by": "source coordinates", "image": "",
                "osm_kind": p["osm_kind"],
            })
        before = len(cands)
        cands = merge(cands, extra)
        print(f"  {len(found)} POIs, {len(cands) - before} were new")
    else:
        print("[4/5] Overpass gap-fill skipped")

    print(f"[5/5] fetching up to {a.images} Wikipedia images ...")
    ranked = sorted(cands, key=lambda c: -len(c.get("desc", "")))
    for c in ranked[:a.images]:
        img, extract = wikipedia_image(c["name"], f"{a.dest} {a.region}")
        if img:
            c["image"] = img
        if extract and len(extract) > len(c.get("desc", "")):
            c["wikipedia_extract"] = extract
    got = sum(1 for c in cands if c["image"])
    print(f"  {got} images found")

    # distance from centre - the scheduler needs to know what is a day trip
    for c in cands:
        if c.get("lat") is not None:
            c["km_from_centre"] = round(
                geo.haversine_km((centre["lat"], centre["lon"]), (c["lat"], c["lon"])), 1)
        else:
            c["km_from_centre"] = None

    g.save()
    payload = {
        "destination": a.dest,
        "region": a.region,
        "centre": centre,
        "wikivoyage_page": title,
        "day_trip_hubs": hubs,
        "harvested": dt.date.today().isoformat(),
        "candidates": cands,
    }
    out = trip_dir / "candidates.json"
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False))

    stale = sum(1 for c in cands if c["stale"])
    print(f"\n{len(cands)} candidates -> {out}")
    print(f"  {stale} carry stale or missing price/hours data (verify before booking)")
    print(f"  cache: {g.stats()}")


if __name__ == "__main__":
    main()
