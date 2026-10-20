#!/usr/bin/env python3
"""Render plan.json to an A5 PDF you can actually use while moving.

One card per stop: the clock, how long, what it costs, the drive from the
previous stop, a photo, and two tappable links - Directions and Book. Each day
opens with a map of that day's stops in visiting order.

Reads only plan.json, so it runs anywhere - no credentials, no network beyond
map tiles and photos, both cached. Everything is derived from the plan; correct
data in overrides.json and re-run, never here.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import io
import json
import math
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import money    # noqa: E402
import packing  # noqa: E402
import sun    # noqa: E402

TILE_DIR = ROOT / "cache" / "tiles"
PHOTO_DIR = ROOT / "cache" / "photos"
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
UA = {"User-Agent": "itinerary-maker/1.0 (personal trip planning; "
                    "operator contact via hello@guidantoperations.tech)"}
TILE = 256
MAP_W, MAP_H = 760, 300

PALETTE = {"ink": "#1c2430", "muted": "#68727f", "line": "#e3e7ec",
           "accent": "#0e7a6d", "accent_soft": "#e3f2ef",
           "warn": "#b3541e", "warn_soft": "#fbeee4"}


# --------------------------------------------------------------------- tiles
def deg2px(lat, lon, z):
    n = TILE * (2 ** z)
    x = (lon + 180.0) / 360.0 * n
    lat_r = math.radians(max(-85.05, min(85.05, lat)))
    y = (1 - math.log(math.tan(lat_r) + 1 / math.cos(lat_r)) / math.pi) / 2 * n
    return x, y


def fetch_tile(z, x, y):
    TILE_DIR.mkdir(parents=True, exist_ok=True)
    path = TILE_DIR / f"{z}_{x}_{y}.png"
    if path.exists():
        return path
    try:
        req = urllib.request.Request(TILE_URL.format(z=z, x=x, y=y), headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            path.write_bytes(r.read())
        return path
    except Exception:
        return None


def render_map(points, width=MAP_W, height=MAP_H):
    """A static map with numbered pins in visiting order. '' if unavailable."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return ""
    pts = [(p["lat"], p["lon"]) for p in points if p.get("lat") is not None]
    if not pts:
        return ""

    lats = [p[0] for p in pts]; lons = [p[1] for p in pts]
    pad = 0.25
    span_lat = max(max(lats) - min(lats), 0.004) * (1 + pad * 2)
    span_lon = max(max(lons) - min(lons), 0.004) * (1 + pad * 2)
    clat, clon = (max(lats) + min(lats)) / 2, (max(lons) + min(lons)) / 2

    z = 16
    while z > 2:
        n = TILE * (2 ** z)
        if (span_lon / 360.0 * n) <= width and (span_lat / 180.0 * n * 1.4) <= height:
            break
        z -= 1

    cx, cy = deg2px(clat, clon, z)
    left, top = cx - width / 2, cy - height / 2
    canvas = Image.new("RGB", (width, height), "#e8ecef")
    x0, y0 = int(left // TILE), int(top // TILE)
    x1, y1 = int((left + width) // TILE), int((top + height) // TILE)
    for tx in range(x0, x1 + 1):
        for ty in range(y0, y1 + 1):
            tp = fetch_tile(z, tx, ty)
            if not tp:
                continue
            try:
                canvas.paste(Image.open(tp).convert("RGB"),
                             (int(tx * TILE - left), int(ty * TILE - top)))
            except Exception:
                pass

    d = ImageDraw.Draw(canvas, "RGBA")
    screen = []
    for p in points:
        if p.get("lat") is None:
            continue
        px, py = deg2px(p["lat"], p["lon"], z)
        screen.append((px - left, py - top, p))

    for (ax, ay, _), (bx, by, _) in zip(screen, screen[1:]):
        d.line([ax, ay, bx, by], fill=(14, 122, 109, 210), width=4)

    for i, (px, py, p) in enumerate(screen, 1):
        r = 15
        col = (28, 36, 48, 255) if p.get("base") else (14, 122, 109, 255)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col, outline=(255, 255, 255, 255), width=3)
        label = "B" if p.get("base") else str(p.get("n", i))
        try:
            tw = d.textlength(label)
        except Exception:
            tw = 7 * len(label)
        d.text((px - tw / 2, py - 7), label, fill=(255, 255, 255, 255))

    buf = io.BytesIO()
    canvas.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# -------------------------------------------------------------------- photos
def _variants(url):
    """The URL, then the sizes Wikimedia actually pre-renders, then the original.

    Wikimedia rejects thumbnail widths it has not pre-rendered, and which ones
    exist differs per image, so guessing a single width fails most of the time.
    """
    import re as _re
    yield url
    if "/thumb/" in url:
        for w in (500, 1280, 800, 320):
            v = _re.sub(r"/\d+px-", f"/{w}px-", url)
            if v != url:
                yield v
        # Strip the thumb wrapper entirely to reach the original file.
        yield _re.sub(r"/thumb(/.+?)/[^/]+$", r"\1", url)


def photo(url):
    """Inline a remote image as a data URI, cached on disk. '' on failure."""
    if not url:
        return ""
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    # A stable digest, not hash(): Python randomises string hashing per process,
    # so the old key never hit the cache and re-downloaded every single run.
    key = PHOTO_DIR / (hashlib.sha1(url.encode()).hexdigest()[:20] + ".img")
    if key.exists():
        raw = key.read_bytes()
    else:
        raw = None
        for candidate in _variants(url):
            try:
                req = urllib.request.Request(candidate, headers=UA)
                with urllib.request.urlopen(req, timeout=25) as r:
                    data = r.read()
                if 0 < len(data) <= 6_000_000:
                    raw = data
                    break
            except Exception:
                continue
        if raw is None:
            return ""
        key.write_bytes(raw)
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        im.thumbnail((560, 380))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=78)
        raw = buf.getvalue()
    except Exception:
        pass
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode()


def load_tickets(trip_dir):
    """Screenshots the traveller dropped in trips/<slug>/tickets/.

    Boarding passes, Apple Wallet grabs, booking confirmations - anything worth
    having on a phone when there is no signal at the rental desk. Embedded as
    data URIs so the PDF carries them without a network.
    """
    tdir = pathlib.Path(trip_dir) / "tickets"
    if not tdir.is_dir():
        return []
    out = []
    def _natural(f):
        # Lexicographic order put ticket 10 between 1 and 2.
        m = re.match(r"(\d+)", f.stem)
        return (int(m.group(1)) if m else 9999, f.stem)

    for f in sorted(tdir.iterdir(), key=_natural):
        if f.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
            continue
        try:
            raw = f.read_bytes()
            try:
                from PIL import Image
                im = Image.open(io.BytesIO(raw))
                im = im.convert("RGB")
                im.thumbnail((1000, 1500))
                buf = io.BytesIO()
                im.save(buf, "JPEG", quality=82)
                data = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
            except Exception:
                mime = "image/png" if f.suffix.lower() == ".png" else "image/jpeg"
                data = f"data:{mime};base64," + base64.b64encode(raw).decode()
            # The leading number orders the pages; it is not part of the name.
            bare = re.sub(r"^\d+[-_]", "", f.stem)
            label = bare.replace("-", " ").replace("_", " ")
            out.append({"name": label.title(), "stem": f.stem.lower(),
                        "anchor": "ticket-" + re.sub(r"[^a-z0-9]+", "-", bare.lower()).strip("-"),
                        "data": data})
        except Exception:
            continue
    return out


def maps_link(lat, lon, query=""):
    if query:
        return ("https://www.google.com/maps/search/?api=1&query="
                + urllib.parse.quote(query))
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}" if lat else ""


def esc(x):
    return html.escape(str(x or ""))


# ---------------------------------------------------------------------- html
WP_API = "https://en.wikipedia.org/w/api.php"
WP_REST = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def lookup_image(name, where):
    """Find a photo for a stop that the harvest did not cover.

    Harvest fetches images for the highest-description entries, which is not
    the same set as the stops that end up scheduled. This closes that gap for
    the handful of stops actually on the plan.
    """
    import time
    try:
        time.sleep(1.2)
        q = urllib.parse.urlencode({"action": "query", "list": "search",
                                    "srsearch": f"{name} {where}", "srlimit": 1,
                                    "format": "json", "formatversion": 2})
        req = urllib.request.Request(f"{WP_API}?{q}", headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            hits = json.loads(r.read()).get("query", {}).get("search", [])
        if not hits:
            return ""
        time.sleep(1.2)
        title = urllib.parse.quote(hits[0]["title"].replace(" ", "_"))
        req = urllib.request.Request(WP_REST + title, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            summary = json.loads(r.read())
        return ((summary.get("thumbnail") or {}).get("source", "")
                or (summary.get("originalimage") or {}).get("source", ""))
    except Exception:
        return ""


def ticket_note_html(d, ticket, esc):
    """A short operational panel pinned under the ticket it belongs to.

    Rental terms run to pages; what you need standing in an airport is the
    phone number, the door, and the two things that cost money if you get them
    wrong.
    """
    import re as _re

    def flat(x):
        return _re.sub(r"[^a-z0-9]", "", (x or "").lower())

    for note in (d.get("brief", {}).get("ticket_notes") or []):
        if flat(note.get("match", "")) not in flat(ticket.get("stem", "")):
            continue
        out = ['<div class="tnote">']
        if note.get("title"):
            out.append('<div class="tn-h">' + esc(note["title"]) + "</div>")
        for blk in note.get("blocks", []):
            out.append('<div class="tn-b"><div class="tn-t">' + esc(blk["heading"])
                       + "</div><ul>")
            for line in blk.get("lines", []):
                out.append("<li>" + esc(line) + "</li>")
            out.append("</ul></div>")
        out.append("</div>")
        return "".join(out)
    return ""


def choices_html(ch, esc):
    """The 'pick one' block, rendered where the decision happens."""
    out = ['<div class="choices"><div class="ch-h">' + esc(ch["title"]) + "</div>"
           + ('<div class="ch-n">' + esc(ch["note"]) + "</div>" if ch.get("note") else "")]
    for i in ch.get("items", []):
        links = " ".join('<a href="' + esc(u) + '">' + esc(t) + "</a>"
                         for t, u in i.get("links", []))
        out.append('<div class="ch-i"><div class="ch-t">' + esc(i["name"])
                   + ('<span class="ch-c">' + esc(i["cost"]) + "</span>"
                      if i.get("cost") else "")
                   + '</div><div class="ch-w">' + esc(i["why"]) + "</div>"
                   + ('<div class="links">' + links + "</div>" if links else "")
                   + "</div>")
    out.append("</div>")
    return "".join(out)


def build_html(d, with_photos=True, tickets=None, only_group=None):
    P = PALETTE
    b = d["brief"]
    tickets = tickets or []
    # A per-person edition: only the tracks this group is actually on.
    if only_group:
        d = dict(d)
        per = next((x for x in (d.get("people") or [])
                    if x.get("key") == only_group), None)
        # Match a person first, then fall back to a track name. A person's
        # edition must include every day they are on, group days included.
        by_person = [x for x in d["plan"] if only_group in (x.get("members") or [])]
        d["plan"] = by_person or [x for x in d["plan"] if x.get("group") == only_group]
        # Rebuild the packing list against THIS person's days. Otherwise every
        # copy carries the whole party's gear, and a non-skier is told to bring
        # goggles for a day they spend in a hot pool.
        try:
            d["packing"] = packing.build(d)
            # Someone who has not decided yet needs to see what the decision
            # would cost them in luggage - an empty list reads as "nothing to
            # do", and the gear is not rentable at the last minute in a group.
            me = next((x for x in (d.get("people") or [])
                       if x.get("key") == only_group), None)
            if me and me.get("skis") not in (True, False):
                d["packing"] = list(d["packing"]) + [{
                    "section": "Only if you decide to ski",
                    "note": "You are down as undecided. Settle it before the trip - "
                            "outerwear is easier to bring than to find on the day, and "
                            "the lift pass price changes.",
                    "items": [
                        {"item": "Ski jacket and trousers", "priority": "optional",
                         "why": "only if you take the Tuesday afternoon pass"},
                        {"item": "Goggles", "priority": "optional",
                         "why": "flat light on the mountain - sunglasses are not enough"},
                        {"item": "Thermal base layers", "priority": "optional",
                         "why": "only if you ski"},
                        {"item": "Waterproof gloves and ski socks", "priority": "optional",
                         "why": "only if you ski"},
                    ]}]
        except Exception as exc:
            # Never silently ship the whole party's gear list to one person -
            # say so, so the miss is visible instead of plausible.
            print(f"  ! per-person packing failed for {only_group}: "
                  f"{type(exc).__name__}: {exc}")
        # And their own costs, not the trip-wide figure.
        billable = [x for x in d["plan"] if not x.get("alternative")]
        lo = sum(x.get("cost", {}).get("nzd_low", 0) for x in billable)
        hi = sum(x.get("cost", {}).get("nzd_high", 0) for x in billable)
        base_cost = dict(d.get("cost") or {})
        base_cost.update({"nzd_low": lo, "nzd_high": hi, "display": money.fmt(lo, hi),
                          "basis": "for this person - activities and meals only, no "
                                   "accommodation, fuel, or rental car"})
        d["cost"] = base_cost
        # Strip punctuation on both sides before matching: the key "jiyeon"
        # does not appear in the filename "2-ji-yeon-25B" as a substring, and
        # she quietly received everybody's boarding passes.
        import re as _re

        def _flat(x):
            return _re.sub(r"[^a-z0-9]", "", (x or "").lower())

        key_flat = _flat(only_group)
        my_roles = {r.lower() for r in (per or {}).get("roles", [])}
        drives = (per or {}).get("drives", "no")

        def audience_for(stem):
            """Who should be carrying this document.

            A rental agreement is only useful to someone who might drive it,
            and an accommodation booking to whoever has to check the party in.
            Everything else is either personal or genuinely shared.
            """
            for rule in (d.get("brief", {}).get("ticket_rules") or []):
                if _flat(rule.get("match", "")) in _flat(stem):
                    return rule.get("audience", "personal")
            return "personal"

        keep = []
        for t in tickets:
            stem = t.get("stem", "")
            aud = audience_for(stem)
            if aud == "everyone":
                keep.append(t)
            elif aud == "drivers":
                if drives in ("primary", "secondary") or "driver" in " ".join(my_roles):
                    keep.append(t)
            elif aud == "organisers":
                if "organiser" in my_roles or "organizer" in my_roles:
                    keep.append(t)
            elif key_flat and key_flat in _flat(stem):
                keep.append(t)
        tickets = keep
    if with_photos:
        where = f"{d['destination']} {d.get('region', '')}"
        missing = [i for o in d["plan"] for i in o["timeline"]
                   if i["type"] == "stop" and not i.get("image")]
        if missing:
            print(f"  looking up photos for {len(missing)} stops the harvest missed ...")
            for it in missing:
                it["image"] = lookup_image(it["name"], where)
    out = [f"""<meta charset="utf-8"><title>{esc(d['destination'])} itinerary</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="hermes-title" content="{esc(d['destination'])} itinerary">
<meta name="hermes-description" content="{esc(d['brief'].get('days', ''))} days from {esc(d['brief'].get('start_date', ''))} - day options, costs, weather and packing">
<style>
@page {{ size: A5 portrait; margin: 10mm 9mm; }}
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: {P['ink']}; font-size: 10.5px; line-height: 1.45; margin: 0; }}
h1 {{ font-size: 21px; margin: 0 0 2px; }}
h2 {{ font-size: 15px; margin: 0; }}
a {{ color: {P['accent']}; text-decoration: none; }}
.cover {{ padding: 8px 0 14px; border-bottom: 3px solid {P['accent']}; margin-bottom: 12px; }}
.sub {{ color: {P['muted']}; font-size: 11px; }}
.day {{ page-break-before: always; }}
.day:first-of-type {{ page-break-before: avoid; }}
.dayhead {{ background: {P['accent_soft']}; border-left: 4px solid {P['accent']};
            padding: 8px 10px; margin: 0 0 8px; }}
.dayhead .meta {{ color: {P['muted']}; font-size: 9.5px; margin-top: 3px; }}
.warn {{ background: {P['warn_soft']}; color: {P['warn']}; border-left: 4px solid {P['warn']};
         padding: 6px 9px; margin: 6px 0; font-size: 9.5px; font-weight: 600; }}
.map {{ width: 100%; border: 1px solid {P['line']}; border-radius: 6px; margin: 5px 0 7px; }}
.card {{ border: 1px solid {P['line']}; border-radius: 7px; padding: 8px 10px;
         margin-bottom: 7px; page-break-inside: avoid; display: flex; gap: 9px; }}
.card .n {{ flex: 0 0 22px; height: 22px; border-radius: 50%; background: {P['accent']};
            color: #fff; font-weight: 700; font-size: 11px; text-align: center; line-height: 22px; }}
.card .body {{ flex: 1; min-width: 0; }}
.card .t {{ font-weight: 700; font-size: 11.5px; }}
.card .when {{ color: {P['accent']}; font-weight: 700; font-size: 10px; }}
.card .facts {{ color: {P['muted']}; font-size: 9px; margin-top: 2px; }}
.card .desc {{ font-size: 9.5px; margin-top: 4px; }}
.card img {{ width: 92px; height: 68px; object-fit: cover; border-radius: 5px; flex: 0 0 92px; }}
.links a {{ display: inline-block; border: 1px solid {P['accent']}; border-radius: 4px;
            padding: 2px 8px; font-size: 9px; margin: 5px 5px 0 0; font-weight: 600; }}
.meal {{ background: #f6f8f9; border: 1px dashed {P['line']}; border-radius: 6px;
         padding: 5px 9px; margin-bottom: 7px; font-size: 9.5px; color: {P['muted']}; }}
.bench {{ margin-top: 4px; padding-top: 4px; border-top: 1px dotted {P['line']};
          font-size: 8.8px; color: {P['muted']}; }}
.bench b {{ color: {P['ink']}; }}
.verify {{ color: {P['warn']}; font-weight: 600; }}
.opt {{ border: 1px solid {P['line']}; border-radius: 6px; padding: 7px 9px; margin-bottom: 6px;
        page-break-inside: avoid; }}
.opt .h {{ font-weight: 700; font-size: 11px; }}
.wx {{ padding: 5px 9px; border-radius: 5px; margin: 5px 0; font-size: 10px; font-weight: 600; }}
.wx.good {{ background: {P['accent_soft']}; color: {P['accent']}; }}
.wx.bad {{ background: {P['warn_soft']}; color: {P['warn']}; }}
.guide {{ border: 1px dashed {P['muted']}; background: #fbfcfd;
         border-radius: 6px; padding: 7px 9px; margin: 5px 0; }}
.guide .when {{ color: {P['muted']}; font-weight: 600; }}
.fixed {{ border: 1px solid {P['accent']}; background: {P['accent_soft']};
          border-radius: 7px; padding: 7px 9px; margin-bottom: 6px;
          page-break-inside: avoid; }}
.fixed .t {{ font-weight: 700; font-size: 11.5px; }}
.fixed .when {{ color: {P['accent']}; font-weight: 700; font-size: 10px; }}
.fixed .note {{ font-size: 9px; color: {P['muted']}; margin-top: 3px; }}
.pk h3 {{ font-size: 11.5px; margin: 10px 0 4px; color: {P['accent']};
          text-transform: none; letter-spacing: 0; }}
.pk .row {{ display: flex; gap: 7px; align-items: baseline; padding: 2.5px 0;
            border-bottom: 1px dotted {P['line']}; font-size: 9.5px; }}
.pk .box {{ flex: 0 0 10px; height: 10px; border: 1.4px solid {P['muted']};
            border-radius: 2px; }}
.pk .it {{ flex: 1; }}
.pk .why {{ color: {P['muted']}; font-size: 8.6px; }}
.pk .ess {{ color: {P['warn']}; font-weight: 700; font-size: 8.4px; flex: 0 0 auto; }}
.cost {{ display: inline-block; background: {P['accent_soft']}; color: {P['accent']};
         border-radius: 3px; padding: 1px 6px; font-weight: 700; font-size: 9px; }}
.cost.soft {{ background: #f1f3f5; color: {P['muted']}; font-weight: 600; }}
.daycost {{ background: {P['accent_soft']}; border-left: 4px solid {P['accent']};
            padding: 6px 9px; margin: 4px 0 8px; font-size: 10px; font-weight: 700;
            color: {P['accent']}; }}
.orbar {{ background: {P['warn_soft']}; color: {P['warn']}; border: 1px dashed {P['warn']};
         border-radius: 6px; padding: 6px 9px; margin: 0 0 6px; font-weight: 700;
         font-size: 10px; letter-spacing: .04em; }}
.total {{ border: 2px solid {P['accent']}; border-radius: 7px; padding: 9px 11px;
          margin: 8px 0; }}
.total .big {{ font-size: 17px; font-weight: 700; color: {P['accent']}; }}
.toc a {{ display: block; border: 1px solid {P['line']}; border-left: 4px solid {P['accent']};
          border-radius: 6px; padding: 7px 10px; margin-bottom: 6px; color: inherit;
          text-decoration: none; page-break-inside: avoid; }}
.toc .g {{ font-weight: 700; font-size: 10.5px; }}
.toc .acts {{ font-size: 9.3px; color: {P['muted']}; margin-top: 2px; }}
.toc .meta {{ font-size: 8.8px; color: {P['muted']}; margin-top: 2px; }}
.toc .jump {{ float: right; font-size: 8.6px; color: {P['accent']}; font-weight: 700; }}
.datehead {{ font-size: 12px; font-weight: 700; margin: 11px 0 5px; }}
.badge {{ display: inline-block; background: {P['ink']}; color: #fff; border-radius: 3px;
          padding: 1px 7px; font-size: 9px; font-weight: 700; margin-left: 5px; }}
.food {{ border: 1px solid #e6d9c2; background: #fdfaf3; border-left: 4px solid #b3861e;
         border-radius: 7px; padding: 7px 10px; margin-bottom: 6px; page-break-inside: avoid; }}
.food .t {{ font-weight: 700; font-size: 11px; }}
.food .when {{ color: #b3861e; font-weight: 700; font-size: 10px; }}
.food .facts {{ color: {P['muted']}; font-size: 9px; }}
.opt-row {{ display: flex; gap: 6px; align-items: baseline; padding: 3px 0;
            border-top: 1px dotted #e6d9c2; font-size: 9.6px; }}
.opt-row b {{ flex: 0 0 auto; }}
.opt-row .facts {{ flex: 1; }}
.opt-row .mini a {{ font-size: 8.6px; border: 1px solid {P['accent']}; border-radius: 3px;
                    padding: 0 5px; margin-left: 4px; }}
.eat .row {{ display: flex; gap: 8px; padding: 4px 0; border-bottom: 1px dotted {P['line']};
             font-size: 9.4px; page-break-inside: avoid; }}
.eat .nm {{ flex: 1; }}
.eat .pr .mini a {{ font-size: 8.4px; border: 1px solid {P['accent']}; border-radius: 3px;
                    padding: 0 5px; margin-left: 4px; }}
.eat .pr {{ flex: 0 0 auto; color: {P['muted']}; font-size: 9px; }}
.cover {{ position: relative; }}
.corner {{ position: absolute; top: 4px; right: 0; text-align: right; }}
.corner a {{ display: inline-block; background: {P['ink']}; color: #fff; border-radius: 6px;
             padding: 6px 11px; font-size: 9.5px; font-weight: 700; text-decoration: none; }}
.corner .hint {{ font-size: 8px; color: {P['muted']}; margin-top: 3px; }}
.pkcard a {{ display: block; border: 1px solid {P['accent']}; background: {P['accent_soft']};
             border-radius: 6px; padding: 8px 10px; margin: 8px 0 2px; color: inherit;
             text-decoration: none; }}
.pkcard .h {{ font-weight: 700; font-size: 11px; color: {P['accent']}; }}
.pkcard .items {{ font-size: 9.3px; color: {P['ink']}; margin-top: 3px; }}
.pkcard .meta {{ font-size: 8.6px; color: {P['muted']}; margin-top: 2px; }}
.ticket {{ page-break-inside: avoid; }}
.ticket .tcap {{ font-weight: 700; font-size: 11px; color: {P['accent']};
                 border-left: 4px solid {P['accent']}; background: {P['accent_soft']};
                 padding: 5px 9px; margin: 0 0 5px; }}
.ticket .tcap span {{ font-weight: 400; color: {P['muted']}; font-size: 8.6px; }}
.tnote {{ border: 1px solid {P['line']}; border-radius: 7px; padding: 7px 9px;
          margin-top: 7px; page-break-inside: avoid; }}
.tn-h {{ font-weight: 700; font-size: 10.5px; color: {P['accent']}; margin-bottom: 3px; }}
.tn-b {{ margin-top: 4px; }}
.tn-t {{ font-weight: 700; font-size: 9.2px; text-transform: uppercase;
         letter-spacing: .03em; color: {P['ink']}; }}
.tnote ul {{ margin: 1px 0 0; padding-left: 14px; }}
.tnote li {{ font-size: 9px; line-height: 1.35; color: {P['ink']}; }}
.ticket img {{ display: block; max-width: 100%; max-height: 470px; width: auto;
               margin: 0 auto; border: 1px solid {P['line']}; border-radius: 8px; }}
.empty {{ border: 1px dashed {P['line']}; border-radius: 7px; padding: 12px;
          color: {P['muted']}; font-size: 9.5px; }}
.choices {{ border: 1px solid #c8dbd6; background: #f4faf8; border-radius: 7px;
            padding: 8px 10px; margin: 6px 0 8px; page-break-inside: avoid; }}
.ch-h {{ font-weight: 700; font-size: 11px; color: {P['accent']}; }}
.ch-n {{ font-size: 9px; color: {P['muted']}; margin: 2px 0 5px; }}
.ch-i {{ border-top: 1px dotted #c8dbd6; padding: 5px 0 3px; }}
.ch-t {{ font-weight: 700; font-size: 10.3px; }}
.ch-c {{ float: right; color: {P['accent']}; font-weight: 700; font-size: 9px; }}
.ch-w {{ font-size: 9.2px; color: {P['ink']}; margin-top: 1px; }}
.opt .s {{ color: {P['muted']}; font-size: 9px; }}
.chosen {{ border-color: {P['accent']}; background: {P['accent_soft']}; }}
</style>"""]

    corner = ""
    if tickets:
        corner = ('<div class="corner"><a href="#tickets">Tickets &amp; passes &rarr;</a>'
                  '<div class="hint">' + str(len(tickets)) + " saved</div></div>")
    who_line = ""
    if only_group:
        if per:
            bits = []
            if per.get("seat"):
                bits.append("seat " + per["seat"])
            if per.get("roles") and not per.get("hide_roles_on_cover"):
                bits.append(", ".join(per["roles"]))
            who_line = ('<div class="badge" style="margin:6px 0 0 0">'
                        + esc(per.get("short") or per.get("name", "")) + "'s copy</div>"
                        + '<div class="sub" style="margin-top:4px">'
                        + " &middot; ".join(esc(x) for x in bits) + "</div>")
        else:
            who_line = ('<div class="badge" style="margin:6px 0 0 0">'
                        + esc(only_group.replace("-", " ").title()) + "'s copy</div>")
    out.append(f"""<div class="cover">{corner}
<h1>{esc(d['destination'])}</h1>{who_line}
<div class="sub">{b['days']} days from {esc(b['start_date'])} &middot;
{esc(b.get('transport','car'))} &middot; {esc(b.get('pace','moderate'))} pace<br>
Base: {esc(b.get('base',{}).get('name','destination centre'))}</div>
</div>""")

    # An index you can tap. Chrome keeps internal anchors when it prints, so
    # each row jumps straight to that group's page for that day.
    import datetime as _dt

    def slug(day):
        return "d" + day["date"].replace("-", "") + "-" + day.get("group", "all")

    by_date = {}
    for day in d["plan"]:
        by_date.setdefault(day["date"], []).append(day)

    out.append('<div class="toc">')
    for date_iso in sorted(by_date):
        days = by_date[date_iso]
        wthr = days[0]["stats"].get("weather") or {}
        nice = _dt.date.fromisoformat(date_iso).strftime("%A %d %B").replace(" 0", " ")
        wtxt = " &middot; " + esc(wthr.get("summary", "")) if wthr else ""
        out.append('<div class="datehead">' + esc(nice) + wtxt + "</div>")
        for day in days:
            acts = [i["name"] for i in day["timeline"] if i["type"] in ("stop", "fixed")]
            meals = [i.get("suggestion") for i in day["timeline"]
                     if i["type"] == "meal" and i.get("suggestion")]
            size = ""
            cost = "" if b.get("pdf_hide_cost") else day.get("cost", {}).get("display", "")
            eat = " &middot; eat: " + esc(", ".join(m for m in meals if m)) if meals else ""
            out.append(
                '<a href="#' + slug(day) + '"><span class="jump">go to this day &rarr;</span>'
                + '<div class="g">' + esc(day.get("day_title")
                                                          or day.get("group_label", "Everyone"))
                + "</div>"
                + '<div class="acts">' + (esc(" | ".join(acts)) if acts else "nothing scheduled")
                + "</div>"
                + '<div class="meta">' + esc(day["stats"]["starts"]) + "&ndash;"
                + esc(day["stats"]["ends"]) + " &middot; " + esc(cost) + " pp" + eat
                + "</div></a>")
    out.append("</div>")

    # A link to the packing page, with the must-haves shown inline. The brief
    # is the essentials only - the full list is a page away, and nobody reads a
    # forty-item checklist off a contents page.
    people = d.get("people") or []
    if people:
        drivers = [x for x in people if x.get("drives") in ("primary", "secondary")]
        undecided = [x for x in people if x.get("skis") not in (True, False)]
        line = ("Drivers: " + ", ".join(
            (x.get("short", "") + (" (backup)" if x.get("drives") == "secondary" else ""))
            for x in drivers)) if drivers else ""
        tail = ""
        if undecided:
            tail = "still undecided: " + ", ".join(
                x.get("short", "") + " (skiing?)" for x in undecided)
        parts = [esc(x) for x in (line, tail) if x]
        if parts:
            out.append('<div class="meal" style="margin-top:6px">'
                       + " &middot; ".join(parts) + "</div>")

    packing_secs = d.get("packing") or []
    musts = [i["item"] for sec in packing_secs for i in sec["items"]
             if i["priority"] == "essential"]
    total_items = sum(len(sec["items"]) for sec in packing_secs)
    if packing_secs:
        preview = ", ".join(musts[:7]) + ("..." if len(musts) > 7 else "")
        out.append('<div class="pkcard"><a href="#packing">'
                   '<div class="h">Packing list &rarr;</div>'
                   '<div class="items">' + esc(preview) + "</div>"
                   '<div class="meta">' + str(len(musts)) + " essentials of "
                   + str(total_items) + " items - full list at the back</div></a></div>")

    tc = d.get("cost")
    if tc and not b.get("pdf_hide_cost"):
        out.append(f"""<div class="total"><div class="big">{esc(tc['display'])} per adult</div>
<div class="sub">{esc(tc['basis'])}.
{tc['unpriced_items']} item(s) had no findable price and are not in that figure.<br>
{esc(tc['fx_note'])}. Estimates, not quotes - confirm at booking.</div></div>""")

    if b.get("base", {}).get("assumed"):
        out.append('<div class="warn">The base used for every drive time on these pages was '
                   'ASSUMED to be the town centre. Put your real accommodation in brief.json '
                   'and re-run before trusting a single number here.</div>')

    # ---- day pages ----
    for o in d["plan"]:
        st = o["stats"]
        gid = "d" + o["date"].replace("-", "") + "-" + o.get("group", "all")
        out.append('<div class="day" id="' + gid + '">')
        if o.get("alternative"):
            # Say it before the page starts, or two day pages for one date read
            # as two days of plans rather than one choice.
            out.append('<div class="orbar">OR &mdash; instead of the previous page. '
                       'Same day, done differently. Pick one.</div>')
        heading = o.get("day_title") or o.get("group_label", "Everyone")
        who = o.get("group_label", "")
        if o.get("group_size"):
            who += f" ({o['group_size']} people)"
        out.append(f"""<div class="dayhead"><h2>{esc(heading)}</h2><div class="meta" style="font-weight:600;color:#1c2430">Day {o['assigned_day']} &middot; {esc(who)}</div>
<div class="meta">{esc(o['date'])} &middot; sunrise {st['sunrise']}, sunset {st['sunset']}
({st['daylight_hours']}h light) &middot; out {st['starts']}&ndash;{st['ends']}
({st['day_length_hours']}h) &middot; {st['travel_mins']} min moving</div></div>""")
        if o.get("track_note"):
            out.append('<div class="meal" style="font-style:italic">'
                       + esc(o["track_note"]) + "</div>")
        wthr = st.get("weather")
        if wthr:
            cls = "bad" if wthr["band"] in ("wet", "snow") else "good"
            out.append(f'<div class="wx {cls}">{esc(wthr["summary"])}</div>')
        for w in o["warnings"]:
            out.append(f'<div class="warn">{esc(w)}</div>')

        # Fixed anchors are plotted too. On an arrival day every item is fixed,
        # and a map showing only the base pin is a map of nothing.
        located = [i for i in o["timeline"]
                   if i["type"] in ("stop", "fixed") and i.get("lat") is not None
                   and not i.get("bare")]
        pts = [{"lat": d["base"]["lat"], "lon": d["base"]["lon"], "base": True}]
        for i, item in enumerate(located, 1):
            pts.append({"lat": item.get("lat"), "lon": item.get("lon"), "n": i})
        m = render_map(pts)
        if m:
            out.append(f'<img class="map" src="{m}">')

        ch = o.get("choices")
        ch_at = None
        if ch and ch.get("at"):
            hh, mm = ch["at"].split(":")
            ch_at = int(hh) * 60 + int(mm)
        ch_done = False

        n = 0
        for it in o["timeline"]:
            if ch and not ch_done and ch_at is not None and it.get("start", 0) >= ch_at:
                out.append(choices_html(ch, esc))
                ch_done = True
            if it["type"] == "fixed":
                if it.get("lat") is not None:
                    n += 1
                # A soft anchor is a guideline: how long the thing takes and
                # roughly when you would be there. Only the genuinely immovable
                # items - a lift pass, a booked table, the car back at the desk -
                # get to say FIXED, because a page where everything shouts FIXED
                # teaches you to ignore the word.
                pin = f" &middot; map pin {n}" if it.get("lat") is not None else ""
                # The drive in. On a day built entirely from anchors there are no
                # stop cards to carry it, and without it nobody can work out when
                # they get home.
                tm = it.get("travel_mins") or 0
                leg = f" &middot; {tm} min drive" if tm >= 5 else ""
                if it.get("soft"):
                    # Round to five minutes. "around 14:31" is not a guideline,
                    # it is a schedule wearing a guideline's clothes.
                    r5 = lambda m: int(round(m / 5.0) * 5)
                    dur = r5(it.get("duration_min") or 0)
                    when = (f'recommended start time {sun.hhmm(r5(it["start"]))} '
                            f'&middot; allow about {dur} min{leg}{pin}')
                    box = "guide"
                else:
                    when = (f"{sun.hhmm(it['start'])} &ndash; {sun.hhmm(it['end'])} "
                            f"&middot; FIXED{leg}{pin}")
                    box = "fixed"
                if it.get("bare"):
                    # "Dinner" and nothing else. Any header on this card is a
                    # claim about a meal that nobody has booked.
                    if it.get("lat") is not None:
                        n -= 1
                    out.append(f'<div class="guide"><div class="t">{esc(it["name"])}'
                               f'</div></div>')
                    continue
                out.append(f"""<div class="{box}">
<div class="when">{when}</div>
<div class="t">{esc(it['name'])}</div>
{f'<div class="facts">{esc(it["price"])}{f" &middot; <span class=\'cost\'>{esc(money.fmt(it["cost"]["nzd_low"], it["cost"]["nzd_high"]))} pp</span>" if it.get("cost") else ""}</div>' if it.get('price') else ''}
{f'<div class="desc" style="font-size:9.5px">{esc(it["desc"][:220])}</div>' if it.get('desc') else ''}
{f'<div class="note">{esc(it["note"])}</div>' if it.get('note') else ''}
<div class="links">
{f'<a href="{esc(it["link_to"])}">{esc(it.get("link_label","Open the map"))}</a>' if it.get('link_to') else (f'<a href="{maps_link(it.get("lat"), it.get("lon"), it.get("maps_query", ""))}">Directions</a>' if it.get('lat') else '')}
{f'<a href="{esc(it["url"])}">Open</a>' if it.get('url') else ''}
</div></div>""")
            elif it["type"] == "stop":
                n += 1
                img = photo(it.get("image")) if with_photos else ""
                facts = [f"{it['duration_min']} min here",
                         f"{it['travel_mins']} min from the last stop"
                         + ("" if it.get("travel_how") == "routed" else " (estimated)")]
                c = it.get("cost")
                if c:
                    chip = "cost soft" if c["confidence"] == "low" else "cost"
                    facts.append(f'<span class="{chip}">'
                                 f'{esc(money.fmt(c["nzd_low"], c["nzd_high"]))} pp</span>')
                if it.get("price"):
                    facts.append(esc(it["price"]))
                else:
                    facts.append('<span style="color:#98a1ab">no price found</span>')
                stale = it.get("stale") and it.get("price") and c and c["confidence"] == "low"
                out.append(f"""<div class="card"><div class="n">{n}</div><div class="body">
<div class="when">{sun.hhmm(it['start'])} &ndash; {sun.hhmm(it['end'])}</div>
<div class="t">{esc(it['name'])}</div>
<div class="facts">{' &middot; '.join(facts)}
{'<span class="verify"> &middot; price not verified</span>' if stale else ''}</div>
{f'<div class="desc">{esc(it["desc"][:230])}</div>' if it.get('desc') else ''}
<div class="links">
{f'<a href="{maps_link(it.get("lat"), it.get("lon"), it.get("maps_query", ""))}">Directions</a>' if it.get('lat') else ''}
{f'<a href="{esc(it["url"])}">Book / info</a>' if it.get('url') else ''}
</div>""")
                bench = it.get("bench") or []
                if bench:
                    items = " &nbsp;|&nbsp; ".join(
                        f"<b>{esc(x['name'])}</b> ({esc(', '.join(x['why']))})" for x in bench[:3])
                    out.append(f'<div class="bench">Back pocket: {items}</div>')
                out.append("</div>" + (f'<img src="{img}">' if img else "") + "</div>")
            elif it["type"] == "meal":
                # Nothing is booked, so the card does not pretend otherwise. It
                # points at the food page and, outside Queenstown, names the one
                # place worth knowing about in that area.
                opts = it.get("options") or []
                areas = {o_.get("area") for o_ in opts if o_.get("area")}
                hl = ""
                far = [o_ for o_ in opts
                       if o_.get("area") and o_["area"] != "Queenstown"]
                if far and all(o_.get("area") != "Queenstown" for o_ in opts[:1]):
                    o_ = far[0]
                    lk = ('<a href="' + esc(o_["url"]) + '">' + esc(o_["name"]) + "</a>"
                          if o_.get("url") else esc(o_["name"]))
                    hl = ('<div class="facts">' + esc(o_["area"]) + " highlight: "
                          + lk + "</div>")
                out.append(
                    '<div class="food"><div class="when">' + sun.hhmm(it["start"])
                    + " &ndash; " + sun.hhmm(it["end"]) + " &middot; " + esc(it["name"])
                    + '</div><div class="t">Nothing booked &mdash; '
                    + '<a href="#eat">see Food &amp; drink</a></div>' + hl + "</div>")
            elif it["type"] == "return":
                if (it.get("travel_mins") or 0) < 5:
                    continue
                out.append(f'<div class="meal"><b>Drive home</b> &middot; leave about '
                           f'{sun.hhmm(int(round(it["start"] / 5.0) * 5))} '
                           f'&middot; {it["travel_mins"]} min &middot; '
                           f'back at base around {sun.hhmm(int(round(it["end"] / 5.0) * 5))}'
                           f'</div>')
        if ch and not ch_done:
            out.append(choices_html(ch, esc))

        out.append("</div>")

    # ---- the menu of other options ----
    ideas = d.get("ideas") or []
    if ideas:
        out.append('<div class="day"><div class="dayhead"><h2>Other things you could do</h2>'
                   '<div class="meta">Swap any of these in. Every link was checked and '
                   'working when this was generated.</div></div>')
        for i in ideas:
            links = " ".join('<a href="' + esc(u) + '">' + esc(t) + "</a>"
                             for t, u in i.get("links", []))
            out.append('<div class="opt"><div class="h">' + esc(i["name"]) + "</div>"
                       + '<div class="s" style="margin-top:3px">' + esc(i["why"]) + "</div>"
                       + ('<div class="s" style="color:#0e7a6d;font-weight:700">'
                          + esc(i["cost"]) + "</div>" if i.get("cost") else "")
                       + '<div class="links">' + links + "</div></div>")
        out.append("</div>")

    eats = d.get("dining") or []
    if eats:
        out.append('<div class="day eat" id="eat"><div class="dayhead"><h2>Food &amp; drink</h2>'
                   '<div class="meta">Nothing here is booked. Every entry links straight to '
                   'the venue and to a map.</div></div>')
        order = ["Queenstown", "Frankton", "Arrowtown", "Gibbston", "Wanaka"]
        by_area = {}
        for e in eats:
            by_area.setdefault(e.get("area") or "Queenstown", []).append(e)
        for area in order + [a for a in by_area if a not in order]:
            rows = by_area.get(area)
            if not rows:
                continue
            highlight = any(r.get("highlight_only") for r in rows)
            label = area + (" &mdash; highlight" if highlight else "")
            out.append('<h3 style="margin:9px 0 3px;color:#0e7a6d;font-size:11px">'
                       + label + "</h3>")
            for e in (rows[:1] if highlight else rows):
                c = e.get("cost")
                pr = money.fmt(c["nzd_low"], c["nzd_high"]) if c else "price not found"
                ml = maps_link(e.get("lat"), e.get("lon"), e.get("maps_query", ""))
                links = ""
                if e.get("url"):
                    links += '<a href="' + esc(e["url"]) + '">site</a>'
                if ml:
                    links += '<a href="' + ml + '">map</a>'
                meal = (" &middot; " + esc(e["meal"])) if e.get("meal") else ""
                out.append('<div class="row"><div class="nm"><b>' + esc(e["name"])
                           + "</b>" + meal
                           + '<div style="color:#68727f;font-size:8.7px">'
                           + esc(e["desc"][:140]) + "</div></div>"
                           + '<div class="pr">' + esc(pr)
                           + '<span class="mini">' + links + "</span></div></div>")
        out.append("</div>")

    packing_pages = d.get("packing") or []
    if packing_pages:
        out.append('<div class="day pk" id="packing"><div class="dayhead"><h2>Packing list</h2>'
                   '<div class="meta">Built from your forecast and the stops actually on '
                   'your plan - not a generic winter list. Essentials are marked.</div></div>')
        order = {"essential": 0, "recommended": 1, "optional": 2}
        for sec in packing_pages:
            out.append(f"<h3>{esc(sec['section'])}</h3>")
            if sec.get("note"):
                out.append(f'<div class="why" style="margin-bottom:4px">{esc(sec["note"])}</div>')
            for i in sorted(sec["items"], key=lambda x: order.get(x["priority"], 3)):
                flag = '<span class="ess">MUST</span>' if i["priority"] == "essential" else ""
                out.append(f'<div class="row"><div class="box"></div>'
                           f'<div class="it">{esc(i["item"])}'
                           f'<div class="why">{esc(i["why"])}</div></div>{flag}</div>')
        out.append("</div>")

    if tickets:
        # One ticket per page, each its own page block. The sibling-break
        # approach kept emitting a stray blank page; the .day mechanism is
        # already proven across this document.
        for idx, t in enumerate(tickets):
            ids = ' id="' + t.get("anchor", "ticket-" + str(idx)) + '"'
            out.append('<div class="day ticket"' + ids + '>'
                       + ('<span id="tickets"></span>' if idx == 0 else "")
                       + '<div class="tcap">' + esc(t["name"])
                       + ' <span>on your phone even with no signal &middot; '
                       + str(idx + 1) + " of " + str(len(tickets)) + "</span></div>"
                       + '<img src="' + t["data"] + '">'
                       + ticket_note_html(d, t, esc) + "</div>")

    out.append(f'<div class="meal" style="margin-top:10px">Generated {esc(d["generated"])}. '
               f'Prices and opening hours come from open data of varying age &mdash; anything '
               f'marked as unverified needs a check before you rely on it. Drive times are real '
               f'routes, not estimates, unless a leg says so.</div>')
    return "\n".join(out)


def chrome():
    for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        from shutil import which
        if which(c):
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trip", required=True)
    ap.add_argument("--out", default="")
    ap.add_argument("--no-photos", action="store_true")
    ap.add_argument("--html", action="store_true",
                    help="also write a browser-readable .html next to the PDF")
    ap.add_argument("--group", default="",
                    help="render only one group's tracks, e.g. --group skiers")
    ap.add_argument("--split", action="store_true",
                    help="write one PDF per group as well as the combined one")
    a = ap.parse_args()

    trip_dir = ROOT / "trips" / a.trip
    d = json.loads((trip_dir / "plan.json").read_text())
    tickets = load_tickets(trip_dir)
    if tickets:
        print(f"tickets: {len(tickets)} image(s) from {trip_dir / 'tickets'}")
    else:
        print(f"tickets: none yet - drop screenshots into {trip_dir / 'tickets'}")

    dest_dir = pathlib.Path(a.out).parent if a.out else pathlib.Path("/root/Documents/Hermes")
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Which editions to produce. --split gives every group its own copy, so a
    # non-skier is not carrying eleven pages about a ski day.
    editions = [(a.group or None, a.out)]
    if a.split:
        # One edition per PERSON where membership is declared, otherwise per
        # track. A non-skier should not be carrying eleven pages about a ski day.
        people = [x["key"] for x in (d.get("people") or []) if x.get("key")]
        if not people:
            for day in d["plan"]:
                for m in (day.get("members") or []):
                    if m not in people:
                        people.append(m)
        if not people:
            for day in d["plan"]:
                gk = day.get("group")
                if gk and gk not in people:
                    people.append(gk)
        editions = [(None, a.out)] + [(x, "") for x in people]

    for group, explicit_out in editions:
        suffix = f"-{group}" if group else ""
        out = (pathlib.Path(explicit_out) if explicit_out
               else dest_dir / f"{a.trip}-itinerary{suffix}.pdf")
        per_l = next((x for x in (d.get("people") or []) if x.get("key") == group), None)
        label = (per_l.get("short") if per_l else group) or "everyone"
        print(f"building pages [{label}] ...")
        doc = build_html(d, with_photos=not a.no_photos, tickets=tickets,
                         only_group=group)
        render_one(doc, out, a.html)
    return


def render_one(doc, out, also_html):
    out.parent.mkdir(parents=True, exist_ok=True)

    if also_html:
        html_out = out.with_suffix(".html")
        html_out.write_text(doc)
        print(f"wrote {html_out}  ({html_out.stat().st_size // 1024} KB)")

    browser = chrome()
    if not browser:
        html_out = out.with_suffix(".html")
        html_out.write_text(doc)
        print(f"no Chrome found - wrote {html_out} instead")
        return

    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / "itin.html"
        src.write_text(doc)
        cmd = [browser, "--headless", "--disable-gpu", "--no-sandbox",
               "--no-pdf-header-footer", f"--print-to-pdf={out}", src.as_uri()]
        r = subprocess.run(cmd, capture_output=True, timeout=180)
        if not out.exists():
            sys.exit(f"chrome failed: {r.stderr.decode()[:500]}")
    print(f"wrote {out}  ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
