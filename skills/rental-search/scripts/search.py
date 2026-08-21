#!/usr/bin/env python3
"""On-demand Sydney rental search, run from a personal machine.

Why a laptop: domain.com.au and realestate.com.au return 403/429 to datacentre
IPs, so the server pipeline has to pay a scraping service to reach them. A
residential connection reads them directly, for nothing. This script is the
free, on-demand counterpart to the server cron - the cron is the passive
monitor, this is the search you drive yourself.

It is deliberately a plain script rather than agent tool-calls, so it behaves
identically under Claude Code and Codex.

Usage:
  python3 search.py                 # search, print, ask before writing
  python3 search.py --write         # search and write to the sheet
  python3 search.py --show-all      # include the near-misses and rejects
  python3 search.py --no-sheet      # skip the sheet entirely, just print
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import browser     # noqa: E402
import sheets      # noqa: E402
import walking     # noqa: E402

CONFIG = json.loads((ROOT / "config.json").read_text())
DATA = ROOT / "data"
STATIONS = json.loads((DATA / "stations.json").read_text())
SUPERMARKETS = [s for s in json.loads((DATA / "supermarkets.json").read_text())
                if s.get("major")]
BUILDINGS = json.loads((DATA / "buildings.json").read_text())
WALK = walking.WalkCache(ROOT / "walk-cache.json")
KEY = ROOT / CONFIG["service_account_key"]

SESSION = None          # the live browser, opened by main()


def fetch(url):
    """Fetch one page through the real browser. Returns html text or None.

    There is deliberately no urllib fallback. A plain GET is refused by both
    sites before it is even read - browser.py records the detail - so a fallback
    would only add a guaranteed failure to every run. A block is still a block:
    if the browser is refused too, we say so rather than inventing a result.
    """
    if SESSION is None:
        raise RuntimeError("fetch() called before the browser session opened")
    return SESSION.get(url)


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------
def json_blobs(page):
    """Yield every embedded JSON object worth searching for listing records."""
    for pat in (r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',
                r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});'):
        for m in re.finditer(pat, page, re.S):
            try:
                yield json.loads(html.unescape(m.group(1)))
            except Exception:
                continue


def walk_json(node, out):
    """Depth-first hunt for dicts that look like a rental listing."""
    if isinstance(node, dict):
        keys = set(node)
        if ("listingType" in keys or "listingId" in keys or "id" in keys) and (
                {"address", "addressParts", "displayAddress"} & keys or
                {"price", "priceDetails", "priceText"} & keys):
            out.append(node)
        for v in node.values():
            walk_json(v, out)
    elif isinstance(node, list):
        for v in node:
            walk_json(v, out)


LISTING_URL = re.compile(
    r'https?://www\.domain\.com\.au/[a-z0-9\-]+-(\d{6,})(?:[?#]|")', re.I)
REA_URL = re.compile(
    r'https?://www\.realestate\.com\.au/property-[a-z\-]+-nsw-[a-z%+\-]+-(\d{6,})', re.I)
PRICE = re.compile(r"\$\s*([\d,]{3,6})")


def parse_domain(page, suburb):
    """Domain embeds listings in __NEXT_DATA__; fall back to link scraping."""
    found, seen = [], set()
    for blob in json_blobs(page):
        cand = []
        walk_json(blob, cand)
        for c in cand:
            lid = str(c.get("listingId") or c.get("id") or "")
            if not lid.isdigit() or lid in seen:
                continue
            seen.add(lid)
            found.append(normalise_domain(c, lid, suburb))
    if found:
        return [f for f in found if f]
    # fallback: at least surface the URLs so a human can look
    for m in LISTING_URL.finditer(page):
        lid = m.group(1)
        if lid in seen:
            continue
        seen.add(lid)
        found.append({"listing_id": lid, "url": m.group(0).rstrip('"'),
                      "suburb": suburb, "source": "domain",
                      "price_pw": None, "beds": None, "address": "",
                      "lat": None, "lon": None, "text": "", "partial": True})
    return found


def dig(d, *names):
    for n in names:
        if isinstance(d, dict) and d.get(n) not in (None, ""):
            return d[n]
    return None


def normalise_domain(c, lid, suburb):
    addr = dig(c, "address", "displayAddress", "addressParts") or {}
    if isinstance(addr, str):
        line, lat, lon, sub = addr, None, None, suburb
    else:
        line = dig(addr, "displayAddress", "streetAddress", "street") or ""
        lat = dig(addr, "lat", "latitude")
        lon = dig(addr, "lng", "longitude")
        sub = dig(addr, "suburb") or suburb
    price_raw = str(dig(c, "priceText", "displayPrice", "price",
                        "priceDetails") or "")
    nums = [int(n.replace(",", "")) for n in PRICE.findall(price_raw)]
    nums = [n for n in nums if 200 <= n <= 3000]
    text = " ".join(str(dig(c, "headline", "title") or "")
                    for _ in (1,)) + " " + str(dig(c, "description", "summary") or "")
    return {"listing_id": lid,
            "url": f"https://www.domain.com.au/{dig(c, 'listingSlug') or ''}"
                   if dig(c, "listingSlug") else
                   f"https://www.domain.com.au/property-profile/{lid}",
            "suburb": sub, "source": "domain",
            "price_pw": min(nums) if nums else None,
            "beds": dig(c, "bedrooms", "beds"),
            "address": line, "lat": lat, "lon": lon,
            "text": text.lower(), "partial": False}


def parse_rea(page, suburb):
    found, seen = [], set()
    for blob in json_blobs(page):
        cand = []
        walk_json(blob, cand)
        for c in cand:
            lid = str(c.get("id") or c.get("listingId") or "")
            if not lid.isdigit() or lid in seen:
                continue
            seen.add(lid)
            addr = c.get("address") or {}
            price_raw = str(dig(c, "price", "displayPrice", "priceText") or "")
            nums = [int(n.replace(",", "")) for n in PRICE.findall(price_raw)]
            nums = [n for n in nums if 200 <= n <= 3000]
            geo = (addr.get("location") or {}) if isinstance(addr, dict) else {}
            found.append({
                "listing_id": lid,
                "url": f"https://www.realestate.com.au/property-{lid}",
                "suburb": (addr.get("suburb") if isinstance(addr, dict) else None)
                          or suburb,
                "source": "rea",
                "price_pw": min(nums) if nums else None,
                "beds": dig(c, "bedrooms", "beds"),
                "address": (addr.get("display") or {}).get("fullAddress", "")
                           if isinstance(addr, dict) else "",
                "lat": geo.get("latitude"), "lon": geo.get("longitude"),
                "text": str(dig(c, "description", "title") or "").lower(),
                "partial": False})
    if not found:
        for m in REA_URL.finditer(page):
            lid = m.group(1)
            if lid in seen:
                continue
            seen.add(lid)
            found.append({"listing_id": lid, "url": m.group(0), "suburb": suburb,
                          "source": "rea", "price_pw": None, "beds": None,
                          "address": "", "lat": None, "lon": None,
                          "text": "", "partial": True})
    return found


# --------------------------------------------------------------------------
# assessment - same rules as the server pipeline
# --------------------------------------------------------------------------
GOOD = {"modern": r"\bmodern\b|\bcontemporary\b",
        "light filled": r"\blight[- ]filled\b|\bsun[- ]drenched\b|\bfloor[- ]to[- ]ceiling\b",
        "spacious": r"\bspacious\b|\boversized\b|\bgenerous(?:ly)?\b",
        "brand new": r"\bbrand[- ]new\b|\bnewly (?:built|completed)\b",
        "renovated": r"\brenovated\b|\brefurbished\b",
        "gym/pool": r"\bgym\b|\bswimming pool\b|\bgymnasium\b"}
BAD = {"compact": r"\bcompact\b|\bcosy\b|\bcozy\b",
       "original condition": r"\boriginal condition\b|\bneeds? (?:work|tlc)\b",
       "dated": r"\bdated\b|\bold[- ]style\b"}
STUDY = r"\bstudy\b|\bhome office\b|\bmulti[- ]purpose room\b"
FLOOR_TEXT = re.compile(
    r"(?:level|floor|lvl)\s*[:\-]?\s*(\d{1,2})\b|\b(\d{1,2})(?:st|nd|rd|th)\s*floor\b",
    re.I)
UNIT = re.compile(r"^\s*([A-Za-z]{0,3}[0-9]{1,5}[A-Za-z]?)\s*/")
GROUND = re.compile(r"^(G|GF|B|LG|UG|SL)[0-9]", re.I)


def building_levels(lat, lon):
    if lat is None or lon is None:
        return None
    best, best_m = None, 45
    for b in BUILDINGS:
        if abs(b["lat"] - lat) > 0.0006 or abs(b["lon"] - lon) > 0.0006:
            continue
        d = walking.haversine_m(lat, lon, b["lat"], b["lon"])
        if d < best_m:
            best, best_m = b, d
    return best["levels"] if best else None


def assess(r):
    """Attach floor, walks and quality. Never drops anything - classification
    only, so a good listing can never be silently hidden."""
    t = r.get("text") or ""
    hits, q = [], 0.0
    for label, pat in GOOD.items():
        if re.search(pat, t):
            hits.append(label)
            q += 1.5 if label in ("modern", "light filled") else 1
    for label, pat in BAD.items():
        if re.search(pat, t):
            hits.append("avoid: " + label)
            q -= 2
    r["quality"], r["signals"] = round(q, 1), ", ".join(hits)
    r["study"] = "yes" if re.search(STUDY, t) else ""

    m = FLOOR_TEXT.search(t)
    if m:
        r["floor"], r["floor_note"] = int(m.group(1) or m.group(2)), "stated"
    else:
        um = UNIT.match(r.get("address") or "")
        u = (um.group(1) if um else "").upper()
        if GROUND.match(u):
            r["floor"], r["floor_note"] = 0, "ground/basement"
        elif re.sub(r"[^0-9]", "", u).isdigit() and re.sub(r"[^0-9]", "", u):
            d = re.sub(r"[^0-9]", "", u)
            if len(d) in (3, 4):
                r["floor"], r["floor_note"] = int(d[:-2]), "from unit number"
            elif len(d) <= 2:
                r["floor"], r["floor_note"] = 0, "low-rise unit number"
            else:
                r["floor"], r["floor_note"] = None, "unit number unreadable"
        else:
            lv = building_levels(r.get("lat"), r.get("lon"))
            if lv is not None:
                r["floor"] = None if lv >= CONFIG["min_floor"] else 0
                r["floor_note"] = f"{lv}-storey building (OSM)"
            else:
                r["floor"], r["floor_note"] = None, "unknown - verify"

    if r.get("lat") is not None:
        st, mins, _ = walking.best_walk((r["lat"], r["lon"]), STATIONS, WALK)
        if st:
            r["station"], r["station_walk"] = st["name"], mins
        sm, smins, _ = walking.best_walk((r["lat"], r["lon"]), SUPERMARKETS,
                                         WALK, limit=3)
        if sm:
            r["supermarket_walk"] = smins
    return r


def verdict(r):
    """(tier, failures). tier: match | near | reject."""
    c, f = CONFIG, []
    p = r.get("price_pw")
    if p is not None and not (c["min_price_per_week"] <= p <= c["max_price_per_week"]):
        f.append(f"${p} outside ${c['min_price_per_week']}-{c['max_price_per_week']}")
    b = r.get("beds")
    if b is not None and not (c["min_bedrooms"] <= b <= c["max_bedrooms"]):
        f.append(f"{b} bedrooms")
    if r.get("floor") is not None and r["floor"] < c["min_floor"]:
        f.append(f"floor {r['floor']}")
    w = r.get("station_walk")
    if w is not None and w > c["max_station_walk_mins"]:
        f.append(f"{w:.0f} min to a station")
    sm = r.get("supermarket_walk")
    if sm is not None and sm > c["max_supermarket_walk_mins"]:
        f.append(f"{sm:.0f} min to a supermarket")
    if r.get("quality", 0) < 0:
        f.append("negative wording in the listing")
    return ("match" if not f else "near" if len(f) == 1 else "reject"), f


def score(r):
    s = -(r.get("quality") or 0) * 1.2
    if r.get("study"):
        s -= 3
    if (r.get("beds") or 0) >= 2:
        s -= 3
    w = r.get("station_walk")
    if w is not None:
        s += w / 2.5 + (1.5 if w > CONFIG["prefer_station_walk_mins"] else 0)
    if r.get("supermarket_walk") is not None:
        s += r["supermarket_walk"] / 6
    return s


# --------------------------------------------------------------------------
def load_context():
    """(suppress_ids, ai_output_ids). Overlap with AI Output is FLAGGED, not
    suppressed - that comparison is the whole point of running this."""
    suppress, ai = set(), set()
    if not KEY.exists():
        print(f"[warn] no {KEY.name} - cannot read your sheet, so nothing is "
              "excluded and nothing will be written", file=sys.stderr)
        return suppress, ai
    sid = CONFIG["spreadsheet_id"]
    try:
        for u in sheets.read_links(sid, KEY, [CONFIG["apartments_tab_gid"]]):
            m = re.search(r"-(\d{6,})(?:[?#]|$)", u.split("?")[0])
            if m:
                suppress.add(m.group(1))
    except Exception as exc:
        print(f"[warn] Apartments tab unreadable: {exc}", file=sys.stderr)
    try:
        gid = sheets.ensure_tab(sid, KEY, CONFIG["ai_output_tab"])
        for row in sheets.read_table(sid, KEY, gid):
            lid = str(row.get("listing_id", "")).strip()
            if not lid:
                continue
            ai.add(lid)
            v = str(row.get("verdict", "")).strip().lower()
            if v == "no" or v.startswith("off market"):
                suppress.add(lid)
    except Exception as exc:
        print(f"[warn] AI Output unreadable: {exc}", file=sys.stderr)
    return suppress, ai


def search_urls():
    lo, hi = CONFIG["min_price_per_week"], CONFIG["max_price_per_week"]
    for s in CONFIG["suburbs"]:
        yield ("domain", s["name"],
               f"https://www.domain.com.au/rent/{s['slug']}/?price={lo}-{hi}"
               f"&bedrooms=1-any&ptype=apartment-unit-flat"
               f"&excludedeposittaken=1&sort=dateupdated-desc")
        nice = s["slug"].rsplit("-nsw-", 1)
        yield ("rea", s["name"],
               f"https://www.realestate.com.au/rent/property-apartment-unit+apartment"
               f"-with-{CONFIG['min_bedrooms']}-bedrooms-in-{nice[0]},+nsw+{nice[1]}"
               f"/list-1?maxPrice={hi}&misc=ex-under-contract")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="write without asking")
    ap.add_argument("--no-sheet", action="store_true")
    ap.add_argument("--show-all", action="store_true")
    args = ap.parse_args()

    suppress, ai_ids = ([], set()) if args.no_sheet else load_context()
    suppress = set(suppress)
    print(f"excluding {len(suppress)} already-judged listings; "
          f"{len(ai_ids)} known to the server pipeline\n", file=sys.stderr)

    global SESSION
    rows, pages, blocked = {}, 0, []
    session = browser.Session(
        ROOT / CONFIG.get("browser_profile_dir", "browser-profile"),
        headless=CONFIG.get("headless", True),
        channel=CONFIG.get("browser_channel"),
        delay_seconds=CONFIG["fetch_delay_seconds"])

    # BrowserUnavailable surfaces on __enter__, not on construction, so the
    # guard has to sit outside the `with` rather than around the constructor.
    try:
        with session as SESSION:
            mode = "headless" if CONFIG.get("headless", True) else "visible"
            print(f"  browser up ({mode})", file=sys.stderr)
            for source, suburb, url in search_urls():
                if pages >= CONFIG["max_pages"]:
                    break
                pages += 1
                print(f"  fetching {source:6} {suburb}", file=sys.stderr)
                page = fetch(url)
                slug = f"{source}-{suburb.replace(' ', '-').lower()}"
                if not page:
                    blocked.append(f"{source}/{suburb}")
                    # the refusal page itself is the evidence - keep it
                    if SESSION.last_html:
                        dbg = ROOT / f"debug-blocked-{slug}.html"
                        dbg.write_text(SESSION.last_html[:400000])
                        print(f"    saved {dbg.name}", file=sys.stderr)
                    continue
                got = (parse_domain(page, suburb) if source == "domain"
                       else parse_rea(page, suburb))
                if not got:
                    dbg = ROOT / f"debug-{slug}.html"
                    dbg.write_text(page[:400000])
                    print(f"    parsed 0 - saved {dbg.name} so the parser can be fixed",
                          file=sys.stderr)
                for r in got:
                    if r["listing_id"] in suppress or r["listing_id"] in rows:
                        continue
                    rows[r["listing_id"]] = r
    except browser.BrowserUnavailable as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 1
    finally:
        SESSION = None

    if blocked:
        print(f"\n[warn] blocked or failed: {', '.join(blocked)}", file=sys.stderr)
    if not rows:
        print("No listings parsed. If debug-*.html files were written, send one "
              "over and the parser can be corrected.", file=sys.stderr)
        return 1

    for r in rows.values():
        assess(r)
        r["tier"], r["fails"] = verdict(r)
        r["matches_ai_output"] = "yes - also found by AI Output" if r["listing_id"] in ai_ids else ""
    WALK.save()      # after assess(), which is what actually populates the cache

    matches = sorted([r for r in rows.values() if r["tier"] == "match"], key=score)
    near = sorted([r for r in rows.values() if r["tier"] == "near"], key=score)
    reject = [r for r in rows.values() if r["tier"] == "reject"]

    def line(r):
        fl = r["floor"] if r["floor"] is not None else "unknown"
        why = r["signals"] or "no strong wording"
        return (f"{r['url']} | {r['suburb']} | ${r.get('price_pw') or '?'} | "
                f"{r.get('beds') or '?'} | {fl} | {why}")

    print(f"\n=== {len(matches)} match every requirement ===")
    for r in matches[:CONFIG["target_count"]]:
        print(line(r) + (f"  [{r['matches_ai_output']}]" if r["matches_ai_output"] else ""))
    if near:
        print(f"\n=== {len(near)} miss on exactly one thing ===")
        for r in (near if args.show_all else near[:6]):
            print(line(r) + f"   <-- {r['fails'][0]}")
    print(f"\n({len(reject)} failed two or more requirements - "
          f"run with --show-all to see them)")
    if args.show_all:
        for r in reject:
            print(line(r) + f"   <-- {'; '.join(r['fails'])}")

    overlap = [r for r in rows.values() if r["matches_ai_output"]]
    print(f"\nsanity check: {len(overlap)} of these were also found by the server "
          f"pipeline", file=sys.stderr)

    if args.no_sheet or not KEY.exists():
        return 0
    if not args.write:
        try:
            if input("\nWrite matches + near-misses to the sheet? [y/N] ").strip().lower() != "y":
                return 0
        except EOFError:
            print("(non-interactive: re-run with --write to save)", file=sys.stderr)
            return 0

    cols = ["verdict", "rank", "suburb", "price_pw", "beds", "study", "floor",
            "floor_note", "station", "station_walk_mins", "supermarket_walk_mins",
            "quality", "signals", "tier", "misses", "matches_ai_output",
            "address", "url", "listing_id"]
    out = []
    for i, r in enumerate(matches + near, start=1):
        out.append({"verdict": "", "rank": i, "suburb": r["suburb"],
                    "price_pw": r.get("price_pw"), "beds": r.get("beds"),
                    "study": r.get("study", ""), "floor": r.get("floor"),
                    "floor_note": r.get("floor_note", ""),
                    "station": r.get("station", ""),
                    "station_walk_mins": r.get("station_walk"),
                    "supermarket_walk_mins": r.get("supermarket_walk"),
                    "quality": r.get("quality"), "signals": r.get("signals", ""),
                    "tier": r["tier"], "misses": "; ".join(r["fails"]),
                    "matches_ai_output": r["matches_ai_output"],
                    "address": r.get("address", ""), "url": r["url"],
                    "listing_id": r["listing_id"]})
    gid = sheets.ensure_tab(CONFIG["spreadsheet_id"], KEY, CONFIG["output_tab"])
    sheets.replace(CONFIG["spreadsheet_id"], KEY, cols, out, gid,
                   signature={"listing_id", "rank"})
    sheets.set_yes_no(CONFIG["spreadsheet_id"], KEY, gid, 0, len(out))
    sheets.set_row_highlight(CONFIG["spreadsheet_id"], KEY, gid, len(out), len(cols))
    print(f"wrote {len(out)} rows to '{CONFIG['output_tab']}'", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
