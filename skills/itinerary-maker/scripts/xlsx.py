#!/usr/bin/env python3
"""Render plan.json to a workbook.

Four sheets, in the order you actually use them:

  Your Plan     the recommended mix, day by day, with the clock
  Day Options   every option that was built, so you can swap a whole day
  Bench         alternates per stop, tagged with why you would swap
  Menu          every candidate that scored, so you can build your own

The workbook is the place to disagree with the plan. Nothing here is a verdict.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "lib"))
import money  # noqa: E402
import sun    # noqa: E402

INK = "1C2430"
ACCENT = "0E7A6D"
WARN = "B3541E"
MUTED = "68727F"

H_FILL = PatternFill("solid", fgColor="0E7A6D")
DAY_FILL = PatternFill("solid", fgColor="E3F2EF")
WARN_FILL = PatternFill("solid", fgColor="FBEEE4")
MEAL_FILL = PatternFill("solid", fgColor="F4F6F8")
THIN = Side(style="thin", color="D8DEE5")
BORDER = Border(bottom=THIN)


def style_header(ws, row=1):
    for c in ws[row]:
        if c.value is None:
            continue
        c.font = Font(bold=True, color="FFFFFF", size=10)
        c.fill = H_FILL
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def widths(ws, spec):
    for i, w in enumerate(spec, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def link(cell, url, text):
    cell.value = text
    if url:
        cell.hyperlink = url
        cell.font = Font(color=ACCENT, underline="single", size=10)


def maps_url(lat, lon, query=""):
    """Search by name where we have one - newer venues are not in OSM."""
    import urllib.parse
    if query:
        return ("https://www.google.com/maps/search/?api=1&query="
                + urllib.parse.quote(query))
    if lat is None or lon is None:
        return ""
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"


def freshness(stale, years):
    if years is None:
        return "unknown age"
    if not stale:
        return f"{years}y old"
    return f"{years}y old - VERIFY"


# --------------------------------------------------------------------------
def sheet_plan(wb, d):
    ws = wb.create_sheet("Your Plan")
    ws.append(["Day", "Date", "Time", "What", "Mins", "Travel",
               "Price as quoted", "Est. NZ$ pp", "Hours", "Weather", "Map",
               "Booking / info"])
    style_header(ws)
    widths(ws, [6, 12, 13, 32, 7, 9, 30, 13, 18, 11, 9, 26])

    for o in d["plan"]:
        st = o["stats"]
        who = o.get("group_label", "Everyone")
        size = f" ({o['group_size']} people)" if o.get("group_size") else ""
        ws.append([f"Day {o['assigned_day']}", o["date"], "",
                   f"{who}{size} - {o['title']}", "", "", "", "", "", "", ""])
        r = ws.max_row
        for c in ws[r]:
            c.fill = DAY_FILL
            c.font = Font(bold=True, size=10)
        if o.get("track_note"):
            ws.append(["", "", "", o["track_note"]])
            c = ws.cell(row=ws.max_row, column=4)
            c.font = Font(italic=True, size=9, color=MUTED)
            c.alignment = Alignment(wrap_text=True)
        w = st.get("weather")
        if w:
            ws.append(["", "", "", f"Forecast: {w['summary']}"])
            c = ws.cell(row=ws.max_row, column=4)
            c.font = Font(bold=True, size=9,
                          color=WARN if w["band"] in ("wet", "snow") else ACCENT)
            if w["band"] in ("wet", "snow"):
                c.fill = WARN_FILL
        ws.append(["", "", "", f"sunrise {st['sunrise']} - sunset {st['sunset']} "
                               f"({st['daylight_hours']}h daylight) - "
                               f"day runs {st['starts']}-{st['ends']} "
                               f"({st['day_length_hours']}h), {st['travel_mins']} min moving"])
        ws.cell(row=ws.max_row, column=4).font = Font(italic=True, size=9, color=MUTED)

        for w in o["warnings"]:
            ws.append(["", "", "", f"! {w}"])
            cell = ws.cell(row=ws.max_row, column=4)
            cell.font = Font(bold=True, size=9, color=WARN)
            cell.fill = WARN_FILL

        for it in o["timeline"]:
            if it["type"] == "fixed":
                cost = it.get("cost")
                # Soft anchors are a guideline, so the sheet shows "~09:56" and
                # calls the row a guide - the same distinction the PDF draws.
                soft = it.get("soft")
                when = (f"~{sun.hhmm(it['start'])}" if soft
                        else f"{sun.hhmm(it['start'])}-{sun.hhmm(it['end'])}")
                ws.append(["", "", when,
                           ("\u00b7 " if soft else "\u2691 ") + it["name"],
                           it.get("duration_min", ""),
                           f"{it.get('travel_mins', 0)}m",
                           it.get("price", "") or "-",
                           money.fmt(cost["nzd_low"], cost["nzd_high"]) if cost else "-",
                           "", "guide" if soft else "fixed", "", ""])
                r = ws.max_row
                for c in ws[r]:
                    c.fill = DAY_FILL
                    c.font = Font(bold=True, size=10)
                link(ws.cell(row=r, column=11), maps_url(it.get("lat"), it.get("lon"), it.get("maps_query", "")), "map")
                link(ws.cell(row=r, column=12), it.get("url", ""), "open")
                if it.get("note"):
                    ws.append(["", "", "", f"   {it['note']}"])
                    ws.cell(row=ws.max_row, column=4).font = Font(italic=True, size=9, color=MUTED)
            elif it["type"] == "stop":
                cost = it.get("cost")
                ws.append([
                    "", "", f"{sun.hhmm(it['start'])}-{sun.hhmm(it['end'])}", it["name"],
                    it["duration_min"],
                    f"{it['travel_mins']}m" + (" est" if it.get("travel_how") != "routed" else ""),
                    it.get("price", "") or "no price found",
                    money.fmt(cost["nzd_low"], cost["nzd_high"]) if cost else "-",
                    (it.get("hours", "") or "-")[:40],
                    "indoor" if it.get("indoor") else
                    ("weather-dependent" if it.get("weather_sensitive") else "any"),
                    "", ""])
                r = ws.max_row
                link(ws.cell(row=r, column=11), maps_url(it.get("lat"), it.get("lon"), it.get("maps_query", "")), "map")
                link(ws.cell(row=r, column=12), it.get("url", ""),
                     it.get("url", "") and "open" or freshness(it.get("stale"),
                                                               it.get("source_years_old")))
                if not it.get("price"):
                    ws.cell(row=r, column=7).font = Font(italic=True, size=9, color=MUTED)
                if cost and cost["confidence"] == "low":
                    ws.cell(row=r, column=8).font = Font(color=WARN, size=10)
                if it.get("weather_sensitive") and not it.get("indoor"):
                    ws.cell(row=r, column=10).font = Font(color=WARN, size=10)
                for c in ws[r]:
                    c.border = BORDER
            elif it["type"] == "meal":
                label = it["name"] + (f": {it['suggestion']}" if it.get("suggestion") else "")
                cost = it.get("cost")
                ws.append(["", "", f"{sun.hhmm(it['start'])}-{sun.hhmm(it['end'])}",
                           label, it.get("duration_min", ""), "",
                           it.get("suggestion_price", "") or "no price found",
                           money.fmt(cost["nzd_low"], cost["nzd_high"]) if cost else "-",
                           "", "", "", ""])
                r = ws.max_row
                for c in ws[r]:
                    c.fill = MEAL_FILL
                    c.font = Font(italic=True, size=10)
                link(ws.cell(row=r, column=12), it.get("suggestion_url", ""), "open")
            elif it["type"] == "wait":
                ws.append(["", "", f"{sun.hhmm(it['start'])}-{sun.hhmm(it['end'])}",
                           it["name"], it.get("duration_min", "")])
                ws.cell(row=ws.max_row, column=4).font = Font(italic=True, size=9, color=MUTED)
            elif it["type"] == "return":
                ws.append(["", "", f"{sun.hhmm(it['start'])}-{sun.hhmm(it['end'])}",
                           "Back to base", "", f"{it['travel_mins']}m"])
                ws.cell(row=ws.max_row, column=4).font = Font(italic=True, size=10, color=MUTED)

        dc = o.get("cost")
        if dc:
            ws.append(["", "", "", f"Day {o['assigned_day']} estimate", "", "",
                       f"{dc['priced']} priced, {dc['unpriced']} without a price",
                       dc["display"]])
            r = ws.max_row
            for c in ws[r]:
                c.font = Font(bold=True, size=10, color=ACCENT)
                c.fill = DAY_FILL

        if o.get("dropped"):
            ws.append(["", "", "", "Considered but did not fit:"])
            ws.cell(row=ws.max_row, column=4).font = Font(bold=True, size=9, color=MUTED)
            for dd in o["dropped"][:6]:
                ws.append(["", "", "", f"   {dd['name']} - {dd['drop_reason']}"])
                ws.cell(row=ws.max_row, column=4).font = Font(size=9, color=MUTED)
        ws.append([])
    return ws


def sheet_options(wb, d):
    ws = wb.create_sheet("Day Options")
    ws.append(["Option", "Title", "Kind", "Theme", "Stops", "Runs",
               "Hours", "Driving", "In the mix?", "Watch out for", "Itinerary"])
    style_header(ws)
    widths(ws, [22, 30, 10, 12, 7, 13, 8, 9, 12, 44, 60])

    chosen = set(d.get("recommended", []))
    for o in d["options"]:
        st = o["stats"]
        seq = " -> ".join(i["name"] for i in o["timeline"] if i["type"] == "stop")
        ws.append([o["id"], o["title"], o["kind"], o["theme"], st["stops"],
                   f"{st['starts']}-{st['ends']}", st["day_length_hours"],
                   f"{o['driving_round_trip_mins']}m",
                   "YES" if o["id"] in chosen else "",
                   "; ".join(o["warnings"]), seq])
        r = ws.max_row
        for c in ws[r]:
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=True)
        if o["id"] in chosen:
            ws.cell(row=r, column=9).font = Font(bold=True, color=ACCENT)
            ws.cell(row=r, column=1).fill = DAY_FILL
        if o["warnings"]:
            ws.cell(row=r, column=10).font = Font(size=9, color=WARN)
    ws.append([])
    ws.append(["", "Every option starts and ends at your accommodation, so any day "
                   "can be swapped for any other without breaking the route."])
    ws.cell(row=ws.max_row, column=2).font = Font(italic=True, size=9, color=MUTED)
    return ws


def sheet_bench(wb, d):
    ws = wb.create_sheet("Bench")
    ws.append(["Day", "If you drop...", "Swap in", "Why", "Km away",
               "Mins", "Indoor?", "Price", "Link"])
    style_header(ws)
    widths(ws, [6, 30, 30, 34, 9, 7, 9, 18, 10])

    for o in d["plan"]:
        for it in o["timeline"]:
            if it["type"] != "stop":
                continue
            bench = it.get("bench") or []
            if not bench:
                ws.append([f"Day {o['assigned_day']}", it["name"],
                           "(nothing comparable nearby)", "", "", "", "", "", ""])
                ws.cell(row=ws.max_row, column=3).font = Font(italic=True, size=9, color=MUTED)
                continue
            for i, b in enumerate(bench):
                ws.append([f"Day {o['assigned_day']}" if i == 0 else "",
                           it["name"] if i == 0 else "", b["name"],
                           ", ".join(b["why"]), b["km_away"], b.get("duration_min", ""),
                           "yes" if b.get("indoor") else "no", b.get("price", "") or "-", ""])
                r = ws.max_row
                link(ws.cell(row=r, column=9), b.get("url", ""), "open")
                if any("rain" in w for w in b["why"]):
                    ws.cell(row=r, column=4).font = Font(color=ACCENT, size=10, bold=True)
                for c in ws[r]:
                    c.border = BORDER
        ws.append([])
    return ws


def sheet_menu(wb, d):
    ws = wb.create_sheet("Menu")
    ws.append(["Score", "Name", "Kind", "Themes", "Where", "Km out",
               "Price (verify)", "Hours", "Data age", "Why it scored", "Link"])
    style_header(ws)
    widths(ws, [7, 34, 8, 26, 18, 8, 22, 22, 14, 40, 10])

    for c in d["menu"]:
        ws.append([c["score"], c["name"], c["kind"], ", ".join(c["themes"]),
                   c.get("day_trip_hub") or d["destination"],
                   c.get("km_from_centre"), c.get("price", "") or "-",
                   (c.get("hours", "") or "-")[:40],
                   freshness(c.get("stale"), c.get("source_years_old")),
                   "; ".join(c.get("why", [])), ""])
        r = ws.max_row
        link(ws.cell(row=r, column=11), c.get("url", ""), "open")
        if c.get("seasonal_risk"):
            ws.cell(row=r, column=8).fill = WARN_FILL
        if c.get("stale"):
            ws.cell(row=r, column=9).font = Font(color=WARN, size=9)
        for cell in ws[r]:
            cell.border = BORDER
    return ws


def sheet_packing(wb, d):
    ws = wb.create_sheet("Packing")
    ws.append(["Priority", "Item", "Why it is on this list", "Packed?"])
    style_header(ws)
    widths(ws, [12, 44, 62, 10])

    order = {"essential": 0, "recommended": 1, "optional": 2}
    for sec in d.get("packing", []):
        ws.append([sec["section"]])
        r = ws.max_row
        ws.cell(row=r, column=1).font = Font(bold=True, size=11, color="FFFFFF")
        for c in ws[r]:
            c.fill = PatternFill("solid", fgColor="0E7A6D")
        if sec.get("note"):
            ws.append(["", sec["note"]])
            c = ws.cell(row=ws.max_row, column=2)
            c.font = Font(italic=True, size=9, color=MUTED)
            c.alignment = Alignment(wrap_text=True)
        for i in sorted(sec["items"], key=lambda x: order.get(x["priority"], 3)):
            ws.append([i["priority"], i["item"], i["why"], ""])
            r = ws.max_row
            if i["priority"] == "essential":
                ws.cell(row=r, column=1).font = Font(bold=True, color=WARN, size=10)
            elif i["priority"] == "optional":
                ws.cell(row=r, column=1).font = Font(color=MUTED, size=10)
            ws.cell(row=r, column=3).font = Font(size=9, color=MUTED)
            for c in ws[r]:
                c.border = BORDER
                c.alignment = Alignment(vertical="top", wrap_text=True)
        ws.append([])
    return ws


def sheet_weather(wb, d):
    f = d.get("forecast") or {}
    if not f:
        return None
    ws = wb.create_sheet("Weather")
    ws.append(["Date", "Outlook", "Low", "High", "Feels like", "Rain",
               "Chance", "Snow", "Wind", "Gusts", "Good for outdoors?"])
    style_header(ws)
    widths(ws, [13, 22, 8, 8, 12, 10, 9, 9, 10, 10, 20])
    for day, v in sorted(f.items()):
        ws.append([day, v["description"], v["temp_min"], v["temp_max"],
                   v.get("feels_like_min"), f"{v['rain_mm']} mm",
                   f"{v['rain_chance']}%", f"{v['snow_cm']} cm",
                   f"{v['wind_kmh']} km/h", f"{v.get('gust_kmh', '')} km/h",
                   "yes" if v["outdoor_ok"] else "keep indoor options ready"])
        r = ws.max_row
        for c in ws[r]:
            c.border = BORDER
        if v["band"] in ("wet", "snow"):
            for c in ws[r]:
                c.fill = WARN_FILL
            ws.cell(row=r, column=11).font = Font(bold=True, color=WARN, size=10)
    ws.append([])
    ws.append(["", f"Source: {d.get('forecast_source', 'forecast')} via Open-Meteo, "
                   f"pulled {d.get('generated', '')}. Re-run closer to the day - a "
                   f"forecast this far out moves."])
    ws.cell(row=ws.max_row, column=2).font = Font(italic=True, size=9, color=MUTED)
    return ws


def sheet_dining(wb, d):
    eats = d.get("dining") or []
    if not eats:
        return None
    ws = wb.create_sheet("Where to eat")
    ws.append(["Area", "Name", "Meal", "Est. NZ$ pp", "Km from base",
               "Indoor?", "Notes", "Link", "Map"])
    style_header(ws)
    widths(ws, [13, 32, 11, 14, 13, 10, 54, 9, 8])
    order = {"Queenstown": 0, "Frankton": 1, "Arrowtown": 2, "Gibbston": 3, "Wanaka": 4}
    for e in sorted(eats, key=lambda x: order.get(x.get("area") or "Queenstown", 9)):
        c = e.get("cost")
        ws.append([e.get("area") or "Queenstown", e["name"],
                   e.get("meal") or e.get("kind", ""),
                   money.fmt(c["nzd_low"], c["nzd_high"]) if c else "no price found",
                   e.get("km_from_base"), "yes" if e.get("indoor") else "no",
                   e.get("desc", ""), "", ""])
        r = ws.max_row
        link(ws.cell(row=r, column=8), e.get("url", ""), "open")
        link(ws.cell(row=r, column=9), maps_url(e.get("lat"), e.get("lon"),
                                                e.get("maps_query", "")), "map")
        ws.cell(row=r, column=1).font = Font(bold=True, color=ACCENT, size=9)
        ws.cell(row=r, column=7).font = Font(size=9, color=MUTED)
        for cell in ws[r]:
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    return ws


def sheet_groups(wb, d):
    by = d.get("cost_by_group") or {}
    if not by:
        return None
    ws = wb.create_sheet("Who does what", 1)
    ws.append(["Date", "Group", "People", "Plan", "Runs", "Est. NZ$ pp"])
    style_header(ws)
    widths(ws, [13, 30, 8, 60, 14, 14])
    for o in d["plan"]:
        seq = " -> ".join(i["name"] for i in o["timeline"]
                          if i["type"] in ("stop", "fixed"))
        # An either/or has to say so, or the sheet reads as two days of plans
        # for one date and the totals below look like they do not add up.
        glabel = ("OR - " if o.get("alternative") else "") + o.get("group_label", "Everyone")
        ws.append([o["date"], glabel, o.get("group_size", ""),
                   seq, f"{o['stats']['starts']}-{o['stats']['ends']}",
                   o.get("cost", {}).get("display", "")])
        r = ws.max_row
        for c in ws[r]:
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=True)
        if o.get("primary"):
            ws.cell(row=r, column=2).font = Font(bold=True, color=ACCENT, size=10)
    ws.append([])
    ws.append(["", "Bold groups are the ones you are in. Totals below are per person "
                   "for that group's own track."])
    ws.cell(row=ws.max_row, column=2).font = Font(italic=True, size=9, color=MUTED)
    for gk, agg in by.items():
        ws.append(["", agg["label"], agg.get("size", ""), "", "", agg["display"]])
        ws.cell(row=ws.max_row, column=6).font = Font(bold=True, color=ACCENT, size=10)
    return ws


def sheet_people(wb, d):
    """Who is on the trip and what each of them is responsible for.

    This is the sheet everything else keys off: roles decide who can drive,
    who needs a lift pass, and which edition of the itinerary each person
    carries.
    """
    people = d.get("people") or []
    if not people:
        return None
    ws = wb.create_sheet("People & roles", 1)
    ws.append(["#", "Name", "Goes by", "Seat", "Roles", "Drives?", "Skis?",
               "On which days", "Notes"])
    style_header(ws)
    widths(ws, [4, 26, 13, 7, 30, 12, 12, 42, 40])

    day_lookup = {}
    for day in d.get("plan", []):
        for m in (day.get("members") or []):
            day_lookup.setdefault(m, []).append(
                f"{day['date'][-5:]} {day.get('group_label', '')}")

    for i, per in enumerate(people, 1):
        skis = per.get("skis")
        skis_txt = {True: "yes", False: "no"}.get(skis, str(skis).upper())
        drives = per.get("drives", "no")
        drives_txt = {"primary": "YES - main driver", "secondary": "backup driver",
                      "no": "no"}.get(drives, drives)
        ws.append([i, per.get("name", ""), per.get("short", ""), per.get("seat", ""),
                   ", ".join(per.get("roles", [])), drives_txt, skis_txt,
                   "; ".join(day_lookup.get(per.get("key", ""), [])) or "-",
                   per.get("note", "")])
        r = ws.max_row
        if per.get("is_you"):
            for c in ws[r]:
                c.fill = DAY_FILL
            ws.cell(row=r, column=2).font = Font(bold=True, color=ACCENT, size=10)
        if drives != "no":
            ws.cell(row=r, column=6).font = Font(bold=True, color=WARN, size=10)
        if skis not in (True, False):
            ws.cell(row=r, column=7).font = Font(bold=True, color=WARN, size=10)
            ws.cell(row=r, column=7).fill = WARN_FILL
        for c in ws[r]:
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=True)

    ws.append([])
    if d.get("transport_note"):
        ws.append(["", d["transport_note"]])
        c = ws.cell(row=ws.max_row, column=2)
        c.font = Font(italic=True, size=9, color=MUTED)
        c.alignment = Alignment(wrap_text=True)
    ws.append([])
    ws.append(["", "Anything highlighted in the Skis? column is still undecided - "
                   "settle it before booking passes, the price changes."])
    ws.cell(row=ws.max_row, column=2).font = Font(bold=True, size=9, color=WARN)
    return ws


def sheet_readme(wb, d):
    ws = wb.create_sheet("Read me first", 0)
    widths(ws, [3, 100])
    b = d["brief"]
    lines = [
        (f"{d['destination']} - {b['days']} days from {b['start_date']}", "title"),
        ("", ""),
        ("This is a menu, not a verdict.", "h"),
        ("Every day option starts and ends at your accommodation, so you can take Day 1 "
         "from one option and Day 2 from another and the route still works.", ""),
        ("", ""),
        ("How to use it", "h"),
        ("1. 'Day Options' - all the shapes the trip could take. Pick the ones you want.", ""),
        ("2. 'Your Plan' - a suggested mix, with the clock worked out. Re-cut it freely.", ""),
        ("3. 'Bench' - what to swap in when it rains, something is shut, or you are tired.", ""),
        ("4. 'Weather' - the forecast for your exact dates, and which days need a Plan B.", ""),
        ("5. 'Packing' - built from your forecast and your actual stops, not a template.", ""),
        ("6. 'Menu' - everything that scored, if you would rather build your own day.", ""),
        ("", ""),
        ("What you should not trust", "h"),
        ("Prices and opening hours come from Wikivoyage and OpenStreetMap, and many "
         "entries have not been touched in years. The 'Data age' column tells you how "
         "old each one is. Anything marked VERIFY needs a check before you rely on it.", ""),
        ("Drive times are real routes over the road network, not estimates - except "
         "where a leg says 'est', which means the router could not be reached.", ""),
        ("Sunrise and sunset are computed for your exact dates and latitude. Outdoor "
         "stops are never scheduled to finish after dark.", ""),
        ("", ""),
        ("What it costs", "h"),
        (f"{d.get('cost', {}).get('display', 'n/a')} per adult across the trip - "
         f"{d.get('cost', {}).get('basis', '')}. "
         f"{d.get('cost', {}).get('unpriced_items', 0)} items had no findable price and are "
         f"not in that figure. {d.get('cost', {}).get('fx_note', '')}", ""),
        ("", ""),
        ("Base for every route", "h"),
        (f"{b.get('base', {}).get('name', 'destination centre')}", ""),
    ]
    if b.get("base", {}).get("assumed"):
        lines.append(("This base was ASSUMED. Put your real accommodation in brief.json "
                      "and re-run - every drive time on every sheet depends on it.", "warn"))
    lines += [("", ""), (f"Generated {d['generated']} from {len(d['menu'])} scored candidates.", "muted")]

    for text, kind in lines:
        ws.append(["", text])
        c = ws.cell(row=ws.max_row, column=2)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if kind == "title":
            c.font = Font(bold=True, size=16, color=ACCENT)
        elif kind == "h":
            c.font = Font(bold=True, size=11, color=INK)
        elif kind == "warn":
            c.font = Font(bold=True, size=10, color=WARN)
            c.fill = WARN_FILL
        elif kind == "muted":
            c.font = Font(size=9, color=MUTED)
        else:
            c.font = Font(size=10)
        ws.row_dimensions[ws.max_row].height = max(15, 14 * (len(text) // 95 + 1))
    return ws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trip", required=True)
    ap.add_argument("--out", default="")
    a = ap.parse_args()

    d = json.loads((ROOT / "trips" / a.trip / "plan.json").read_text())
    wb = Workbook()
    wb.remove(wb.active)
    sheet_plan(wb, d)
    sheet_options(wb, d)
    sheet_bench(wb, d)
    sheet_weather(wb, d)
    sheet_dining(wb, d)
    sheet_packing(wb, d)
    sheet_menu(wb, d)
    sheet_groups(wb, d)
    sheet_people(wb, d)
    sheet_readme(wb, d)
    wb.active = 0

    out = pathlib.Path(a.out) if a.out else \
        pathlib.Path("/root/Documents/Hermes") / f"{a.trip}-itinerary.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"wrote {out}")
    print(f"  sheets: {', '.join(wb.sheetnames)}")


if __name__ == "__main__":
    main()
