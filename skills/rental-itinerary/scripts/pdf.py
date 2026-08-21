#!/usr/bin/env python3
"""Render plan.json as an illustrated, phone-readable PDF itinerary.

The spreadsheet stays the place you correct data; this is the thing you carry.
A5 portrait so it fills a phone screen, one card per viewing, every link
tappable, and a real map per day so you can see the shape of the trip without
reading a single number.

Maps are stitched from OpenStreetMap tiles - free, no key, and reachable from
this server. Listing photos are NOT: Domain's CDN refuses this host, so photos
are only fetched when --fetch-photos is run from a machine it will serve, and
cached in photos/ from then on. A stop with no cached photo still renders; it
just shows the map pin instead.

Usage:
  python3 pdf.py [plan.json] [-o out.pdf] [--fetch-photos]
"""
from __future__ import annotations

import argparse
import base64
import html
import io
import json
import math
import pathlib
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
PHOTO_DIR = ROOT / "photos"
TILE_DIR = ROOT / "tile-cache"
STATE = pathlib.Path("/root/agentic-workspace/automations/sydney-rentals/state.json")

TILE_UA = {"User-Agent": "sydney-rental-itinerary/1.0 (personal use; "
                         "hello@guidantoperations.tech)"}
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
TILE = 256
MAP_W, MAP_H = 1000, 430          # px, before the browser scales it to the page

PRIORITY_COLOUR = {"High": "#b42318", "Medium": "#b54708", "Low": "#475467"}


# --------------------------------------------------------------------------
# slippy-map maths
# --------------------------------------------------------------------------
def deg2px(lat, lon, z):
    n = TILE * 2 ** z
    x = (lon + 180.0) / 360.0 * n
    s = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return x, y


def fetch_tile(z, x, y):
    n = 2 ** z
    if not (0 <= x < n and 0 <= y < n):
        return None
    path = TILE_DIR / f"{z}_{x}_{y}.png"
    if path.exists():
        return path.read_bytes()
    try:
        req = urllib.request.Request(TILE_URL.format(z=z, x=x, y=y), headers=TILE_UA)
        data = urllib.request.urlopen(req, timeout=20).read()
    except Exception as exc:
        print(f"[warn] tile {z}/{x}/{y}: {exc}", file=sys.stderr)
        return None
    TILE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return data


def dash(d, a, b, colour, seg=14, gap=10, width=4):
    """A dashed segment - PIL has no native dash."""
    (x0, y0), (x1, y1) = a, b
    total = math.hypot(x1 - x0, y1 - y0)
    if total < 1:
        return
    ux, uy = (x1 - x0) / total, (y1 - y0) / total
    t = 0.0
    while t < total:
        e = min(t + seg, total)
        d.line([(x0 + ux * t, y0 + uy * t), (x0 + ux * e, y0 + uy * e)],
               fill=colour, width=width)
        t = e + gap


def spread_coincident(pts, radius_m=90):
    """Fan out pins that share a point so every number stays readable.

    Several properties geocoded to the same suburb centroid would otherwise
    stack into one pin, hiding every stop but the last one drawn.
    """
    out, groups = [], {}
    for p in pts:
        groups.setdefault((round(p["lat"], 4), round(p["lon"], 4)), []).append(p)
    for (la, lo), grp in groups.items():
        if len(grp) == 1:
            out.append(grp[0])
            continue
        dlat = radius_m / 111_320.0
        dlon = dlat / max(math.cos(math.radians(la)), 0.1)
        for i, p in enumerate(grp):
            a = 2 * math.pi * i / len(grp) - math.pi / 2
            q = dict(p)
            q["lat"] = la + dlat * math.sin(a)
            q["lon"] = lo + dlon * math.cos(a)
            out.append(q)
    return out


def render_map(points, width=MAP_W, height=MAP_H, frame_all=False):
    """Stitched OSM map covering `points`, each drawn as a numbered pin.

    points: [{"lat","lon","label","kind"}] - kind "base" draws a dark square,
    anything else a numbered circle in priority colour.

    frame_all=True includes the base when choosing the zoom. That is right for
    the short 'how do I get out there' strip and wrong for the detail map,
    where a base across the city shrinks the day's real stops to specks.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[warn] PIL missing - no maps", file=sys.stderr)
        return None
    pts = [p for p in points if p.get("lat") and p.get("lon")]
    if not pts:
        return None
    pts = spread_coincident(pts)

    # Frame the VIEWINGS, not the base. The base is usually across the city, and
    # letting it set the bounds zooms the day's actual stops down to specks.
    frame = pts if frame_all else ([p for p in pts if p.get("kind") != "base"] or pts)
    lats = [p["lat"] for p in frame]
    lons = [p["lon"] for p in frame]
    z = 16
    while z > 9:
        xs = [deg2px(la, lo, z)[0] for la, lo in zip(lats, lons)]
        ys = [deg2px(la, lo, z)[1] for la, lo in zip(lats, lons)]
        if (max(xs) - min(xs)) < width - 140 and (max(ys) - min(ys)) < height - 140:
            break
        z -= 1

    cx = sum(deg2px(la, lo, z)[0] for la, lo in zip(lats, lons)) / len(frame)
    cy = sum(deg2px(la, lo, z)[1] for la, lo in zip(lats, lons)) / len(frame)
    left, top = cx - width / 2, cy - height / 2

    canvas = Image.new("RGB", (width, height), "#e8e6e1")
    x0, y0 = int(left // TILE), int(top // TILE)
    x1, y1 = int((left + width) // TILE), int((top + height) // TILE)
    for tx in range(x0, x1 + 1):
        for ty in range(y0, y1 + 1):
            raw = fetch_tile(z, tx, ty)
            if not raw:
                continue
            try:
                canvas.paste(Image.open(io.BytesIO(raw)).convert("RGB"),
                             (int(tx * TILE - left), int(ty * TILE - top)))
            except Exception:
                pass

    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 26)
    except Exception:
        font = ImageFont.load_default()

    # legs first, so pins sit on top of the lines
    seq = [p for p in pts if p.get("kind") != "base"]
    xy = [(deg2px(p["lat"], p["lon"], z)[0] - left,
           deg2px(p["lat"], p["lon"], z)[1] - top) for p in seq]
    if len(xy) > 1:
        d.line(xy, fill="#1d4ed8", width=4, joint="curve")

    # the hop out from the base is a different kind of journey - rail, not a
    # walk between viewings - so it gets a dashed line rather than a solid one
    base_pt = next((p for p in pts if p.get("kind") == "base"), None)
    if base_pt and seq:
        bx = deg2px(base_pt["lat"], base_pt["lon"], z)[0] - left
        by = deg2px(base_pt["lat"], base_pt["lon"], z)[1] - top
        dash(d, (bx, by), xy[0], "#1d4ed8")

    for p in pts:
        # the base is drawn only when it happens to fall inside the frame
        if p.get("kind") == "base":
            bx, by = deg2px(p["lat"], p["lon"], z)
            if not (-40 < bx - left < width + 40 and -40 < by - top < height + 40):
                continue
        px, py = deg2px(p["lat"], p["lon"], z)
        px, py = px - left, py - top
        label = str(p.get("label", ""))
        if p.get("kind") == "base":
            d.rectangle([px - 21, py - 21, px + 21, py + 21],
                        fill="#111827", outline="white", width=4)
        else:
            col = PRIORITY_COLOUR.get(p.get("priority"), "#475467")
            d.ellipse([px - 21, py - 21, px + 21, py + 21],
                      fill=col, outline="white", width=4)
        box = d.textbbox((0, 0), label, font=font)
        d.text((px - (box[2] - box[0]) / 2, py - (box[3] - box[1]) / 2 - 3),
               label, fill="white", font=font)

    buf = io.BytesIO()
    canvas.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# --------------------------------------------------------------------------
# photos
# --------------------------------------------------------------------------
BROWSER_UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
    "Accept-Language": "en-AU,en;q=0.9",
}


def scrape_og_image(page_url):
    """Read a listing page's og:image tag.

    The fallback for rows that never came through the watcher - hand-added
    properties have no stored photo urls at all. Needs a connection the site
    will actually serve, so this only ever succeeds from the laptop.
    """
    if not page_url:
        return []
    try:
        req = urllib.request.Request(page_url, headers={
            **BROWSER_UA, "Referer": "https://www.google.com/"})
        html_txt = urllib.request.urlopen(req, timeout=30).read().decode(
            "utf-8", "ignore")
    except Exception as exc:
        print(f"[warn] og:image {page_url[:60]}: {exc}", file=sys.stderr)
        return []
    import re
    return re.findall(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"',
                      html_txt)[:3]


def photo_for(listing_id, images, fetch, page_url=None):
    """Cached photo as a data URI, fetching it first if we are allowed to.

    Returns None rather than a placeholder: an empty frame on every card would
    be worse than a card that simply has no photo.
    """
    if not listing_id:
        return None
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    path = PHOTO_DIR / f"{listing_id}.jpg"
    if not path.exists() and fetch:
        if not images:
            images = scrape_og_image(page_url)
        for u in images or []:
            try:
                req = urllib.request.Request(u, headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/122.0 Safari/537.36",
                    "Referer": "https://www.domain.com.au/"})
                data = urllib.request.urlopen(req, timeout=25).read()
                if len(data) > 2000:
                    path.write_bytes(data)
                    break
            except Exception as exc:
                print(f"[warn] photo {listing_id}: {exc}", file=sys.stderr)
    if not path.exists():
        return None
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


# --------------------------------------------------------------------------
def photo_key(stop):
    """Filename key for a cached photo.

    Domain rows join on their listing id; a realestate.com.au row has none in a
    form we can trust, so it falls back to a hash of its url - stable across
    runs, which is all the cache needs.
    """
    lid = stop.get("listing_id") or ""
    if lid:
        return lid
    link = stop.get("link") or ""
    if not link:
        return ""
    import hashlib
    return "u" + hashlib.sha1(link.encode()).hexdigest()[:12]


def maps_link(stop):
    """A tappable directions link - the point of reading this on a phone."""
    if stop.get("lat") and stop.get("lon"):
        q = f"{stop['lat']},{stop['lon']}"
    else:
        q = stop.get("address") or stop.get("suburb") or ""
    return "https://www.google.com/maps/dir/?api=1&destination=" + \
        urllib.parse.quote(str(q))


def walk_class(rule):
    r = str(rule).lower()
    if r.startswith("over") or "OVER" in str(rule):
        return "bad"
    return "warn" if "estimate" in r else "good"


E = lambda v: html.escape(str(v if v is not None else ""))


def build_html(plan, fetch_photos=False):
    stops = plan["stops"]
    base = plan["base"]
    try:
        state = json.loads(STATE.read_text()) if STATE.exists() else {}
    except Exception:
        state = {}
    days = {}
    for s in stops:
        days.setdefault(s["day"], []).append(s)

    trip = plan.get("trip") or {}
    est = sum(1 for s in stops if str(s.get("located_by", "")).startswith("SUBURB"))
    n_photos = 0

    out = [HEAD]
    out.append(f'''
<section class="cover">
  <p class="kicker">Sydney rental trip</p>
  <h1>Viewing itinerary</h1>
  <p class="dates">{E(trip.get("start",""))} &rarr; {E(trip.get("end",""))}</p>
  <div class="stat-row">
    <div class="stat"><b>{len(stops)}</b><span>viewings</span></div>
    <div class="stat"><b>{len(days)}</b><span>days</span></div>
    <div class="stat"><b>{sum(int(s.get("travel_mins") or 0) for s in stops)}</b>
      <span>min travel</span></div>
  </div>
  <p class="base">All days start from<br><b>{E(base["name"])}</b></p>
  <ul class="legend">
    <li><i class="dot high"></i>High priority</li>
    <li><i class="dot med"></i>Medium</li>
    <li><i class="dot low"></i>Low</li>
    <li><i class="dot sq"></i>Your base</li>
  </ul>
  <p class="caveat">No clock times: agents set those. This gives you the
    <b>order</b> and the <b>hop lengths</b>, so you can slot booked times in and
    see at a glance whether one is reachable from the last.
    {f"<br><b>{est} stop(s)</b> are pinned to a suburb centroid, not a street "
      "address - their walk times are estimates." if est else ""}
    <br>Rail times are modelled at 35 km/h, not looked up. Sequence-grade, not
    Opal-grade.</p>
</section>''')

    for day, items in days.items():
        base_pin = {"lat": base["lat"], "lon": base["lon"], "label": "B",
                    "kind": "base"}
        pts = [base_pin]
        for s in items:
            pts.append({"lat": s.get("lat"), "lon": s.get("lon"),
                        "label": s["stop"], "priority": s.get("priority")})
        # Two maps, because they answer two different questions. The strip shows
        # the run out from the hotel to the first viewing; the detail map shows
        # what the day looks like once you are there. One map cannot do both -
        # a frame wide enough to hold the hotel makes the stops unreadable.
        first = next((q for q in pts[1:] if q.get("lat")), None)
        ctx = render_map([base_pin, first], width=1000, height=250,
                         frame_all=True) if first else None
        img = render_map(pts)
        mins = sum(int(s.get("travel_mins") or 0) for s in items)
        out.append(f'''
<section class="day">
  <header class="dayhead">
    <h2>{E(day)}</h2>
    <p>{len(items)} viewing{"s" if len(items) != 1 else ""}
       &middot; {mins} min travelling
       &middot; {E(", ".join(dict.fromkeys(s["suburb"] for s in items)))}</p>
  </header>
  {f"""<div class="ctx">
    <p class="ctxlabel"><b>B</b> {E(base["name"])}
      <span class="arrow">&rarr;</span> <b>1</b> {E(items[0].get("suburb",""))}
      <span class="ctxvia">{E(items[0].get("travel_via",""))} &middot;
      {E(items[0].get("travel_mins",""))} min</span></p>
    <img class="ctxmap" src="{ctx}" alt="hotel to first stop">
  </div>""" if ctx else ""}
  {f'<img class="map" src="{img}" alt="map">' if img else
   '<p class="nomap">map unavailable</p>'}''')

        for s in items:
            lid = photo_key(s)
            # the plan carries its own urls so this renders anywhere; state.json
            # is only a fallback for plans written before that was true
            imgs = s.get("images") or (state.get(lid) or {}).get("images") or []
            ph = photo_for(lid, imgs, fetch_photos, page_url=s.get("link"))
            n_photos += 1 if ph else 0
            pri = s.get("priority") or "Low"
            wc = walk_class(s.get("walk_rule"))
            suburb_only = str(s.get("located_by", "")).startswith("SUBURB")
            out.append(f'''
  <article class="stop">
    <div class="badge {pri.lower()}">{E(s["stop"])}</div>
    <div class="body">
      <div class="toprow">
        <span class="chip {pri.lower()}">{E(pri)}</span>
        <span class="why">{E(s.get("why_now",""))}</span>
        <span class="price">${E(s.get("cost_pw",""))}<small>/wk</small></span>
      </div>
      <h3>{E(s.get("address") or s.get("suburb"))}</h3>
      <p class="sub">{E(s.get("suburb",""))}
        {'<span class="est">suburb estimate</span>' if suburb_only else ''}</p>
      {f'<img class="photo" src="{ph}" alt="">' if ph else ''}
      <dl class="facts">
        <div><dt>Getting there</dt>
          <dd>{E(s.get("travel_via","")) or "&mdash;"}
            <b>{E(s.get("travel_mins",""))} min</b>
            <span class="from">from {E(s.get("from",""))}</span></dd></div>
        <div><dt>Station</dt>
          <dd>{E(s.get("station","")) or "&mdash;"}
            <span class="walk {wc}">{E(s.get("walk_rule",""))}</span></dd></div>
      </dl>
      {f'<p class="note">{E(s.get("your_comments"))}</p>'
       if s.get("your_comments") else ''}
      <p class="links">
        <a href="{E(s.get("link",""))}">Open listing &#8599;</a>
        <a href="{E(maps_link(s))}">Directions &#8599;</a>
      </p>
    </div>
  </article>''')
        out.append("</section>")

    out.append("</body></html>")
    print(f"[info] {n_photos}/{len(stops)} stops have a cached photo", file=sys.stderr)
    return "\n".join(out)


HEAD = """<!doctype html><html><head><meta charset="utf-8">
<title>Viewing itinerary</title><style>
@page { size: A5 portrait; margin: 10mm 8mm; }
* { box-sizing: border-box; }
body { margin:0; font:13px/1.45 -apple-system,"Segoe UI",Roboto,Helvetica,sans-serif;
       color:#101828; -webkit-print-color-adjust:exact; print-color-adjust:exact; }
h1,h2,h3 { margin:0; line-height:1.15; }
a { color:#1d4ed8; text-decoration:none; }

.cover { page-break-after:always; padding-top:14mm; text-align:center; }
.kicker { margin:0; letter-spacing:.14em; text-transform:uppercase;
          font-size:10px; color:#667085; }
.cover h1 { font-size:34px; margin:6px 0 4px; letter-spacing:-.02em; }
.dates { margin:0 0 20px; color:#475467; font-size:14px; }
.stat-row { display:flex; justify-content:center; gap:10px; margin:0 0 20px; }
.stat { flex:1; border:1px solid #e4e7ec; border-radius:10px; padding:10px 4px; }
.stat b { display:block; font-size:24px; letter-spacing:-.02em; }
.stat span { font-size:9px; text-transform:uppercase; letter-spacing:.08em;
             color:#667085; }
.base { margin:0 0 18px; font-size:13px; color:#475467; }
.legend { list-style:none; display:flex; justify-content:center; gap:12px;
          padding:0; margin:0 0 18px; font-size:10px; color:#475467; }
.dot { display:inline-block; width:9px; height:9px; border-radius:50%;
       margin-right:4px; vertical-align:-1px; }
.dot.high{background:#b42318} .dot.med{background:#b54708}
.dot.low{background:#475467} .dot.sq{background:#111827; border-radius:2px;}
.caveat { font-size:10px; line-height:1.5; color:#667085; text-align:left;
          border-top:1px solid #e4e7ec; padding-top:10px; margin:0; }

.day { page-break-before:always; }
.dayhead { border-bottom:2px solid #101828; padding-bottom:5px; margin-bottom:8px; }
.dayhead h2 { font-size:22px; letter-spacing:-.02em; }
.dayhead p { margin:2px 0 0; font-size:10.5px; color:#667085; }
.ctx { border:1px solid #e4e7ec; border-radius:8px; overflow:hidden;
       margin-bottom:7px; }
.ctxlabel { margin:0; padding:5px 8px; font-size:10px; color:#344054;
            background:#f9fafb; border-bottom:1px solid #e4e7ec; }
.ctxlabel b { display:inline-block; min-width:14px; height:14px; line-height:14px;
              text-align:center; background:#111827; color:#fff; border-radius:3px;
              font-size:9px; margin-right:2px; }
.ctxlabel .arrow { color:#98a2b3; margin:0 3px; }
.ctxvia { color:#667085; float:right; }
.ctxmap { width:100%; display:block; }
.map { width:100%; border-radius:8px; border:1px solid #e4e7ec;
       margin-bottom:9px; display:block; }
.nomap { font-size:10px; color:#98a2b3; }

.stop { display:flex; gap:8px; page-break-inside:avoid; margin-bottom:9px;
        border:1px solid #e4e7ec; border-radius:10px; padding:9px; }
.badge { flex:0 0 26px; height:26px; border-radius:50%; color:#fff;
         font-weight:700; font-size:14px; display:flex; align-items:center;
         justify-content:center; }
.badge.high{background:#b42318} .badge.medium{background:#b54708}
.badge.low{background:#475467}
.body { flex:1; min-width:0; }
.toprow { display:flex; align-items:center; gap:6px; margin-bottom:3px; }
.chip { font-size:8.5px; font-weight:700; text-transform:uppercase;
        letter-spacing:.06em; padding:2px 6px; border-radius:20px; color:#fff; }
.chip.high{background:#b42318} .chip.medium{background:#b54708}
.chip.low{background:#475467}
.why { font-size:9px; color:#667085; }
.price { margin-left:auto; font-weight:700; font-size:15px; }
.price small { font-weight:400; font-size:9px; color:#667085; }
.stop h3 { font-size:14px; letter-spacing:-.01em; }
.sub { margin:1px 0 6px; font-size:10px; color:#667085; }
.est { background:#fef0c7; color:#93370d; padding:1px 5px; border-radius:4px;
       font-size:8.5px; margin-left:4px; }
.photo { width:100%; height:104px; object-fit:cover; border-radius:7px;
         margin-bottom:7px; display:block; }
.facts { margin:0 0 6px; font-size:10.5px; }
.facts div { display:flex; gap:6px; padding:2.5px 0;
             border-top:1px solid #f2f4f7; }
.facts dt { flex:0 0 62px; color:#667085; margin:0; font-size:9.5px;
            padding-top:1px; }
.facts dd { margin:0; flex:1; }
.from { color:#98a2b3; font-size:9px; display:block; }
.walk { display:inline-block; margin-left:4px; padding:1px 5px; border-radius:4px;
        font-size:9px; font-weight:600; }
.walk.good{background:#d1fadf; color:#05603a}
.walk.warn{background:#fef0c7; color:#93370d}
.walk.bad {background:#fee4e2; color:#912018}
.note { margin:0 0 6px; font-size:10.5px; font-style:italic; color:#344054;
        background:#f9fafb; border-left:2px solid #d0d5dd; padding:5px 7px;
        border-radius:0 5px 5px 0; }
.links { margin:0; display:flex; gap:12px; font-size:11px; font-weight:600; }
</style></head><body>"""


def build(plan_path, out_path=None, fetch_photos=False):
    plan = json.loads(pathlib.Path(plan_path).read_text())
    doc = build_html(plan, fetch_photos=fetch_photos)
    out = pathlib.Path(out_path) if out_path else \
        pathlib.Path("/root/Documents/Hermes/viewing-itinerary.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        src = pathlib.Path(td) / "itinerary.html"
        src.write_text(doc)
        cmd = ["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
               "--no-pdf-header-footer", "--virtual-time-budget=15000",
               f"--user-data-dir={td}/profile",
               f"--print-to-pdf={out}", src.as_uri()]
        r = subprocess.run(cmd, capture_output=True, timeout=180)
        if not out.exists() or out.stat().st_size < 1000:
            sys.stderr.write(r.stderr.decode("utf-8", "ignore")[-2000:])
            raise SystemExit("[error] chrome produced no pdf")
    print(f"[info] {out} ({out.stat().st_size // 1024} KB)", file=sys.stderr)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", nargs="?", default=str(ROOT / "plan.json"))
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--fetch-photos", action="store_true")
    a = ap.parse_args()
    build(a.plan, a.out, fetch_photos=a.fetch_photos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
