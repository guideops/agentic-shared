#!/usr/bin/env python3
"""Daily forecast for the trip dates, from Open-Meteo. Free, keyless, cached.

Only useful inside the forecast horizon (about 16 days). Beyond that this
returns climate normals instead and says so, because a made-up forecast for a
trip three months out is worse than no forecast: it invites packing decisions
that have nothing behind them.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import urllib.parse
import urllib.request

FORECAST = "https://api.open-meteo.com/v1/forecast"
CLIMATE = "https://climate-api.open-meteo.com/v1/climate"
UA = {"User-Agent": "itinerary-maker/1.0 (personal trip planning)"}
HORIZON_DAYS = 16

# WMO weather codes, grouped the way a traveller cares about them.
WMO = {
    0: ("Clear", "good"), 1: ("Mainly clear", "good"), 2: ("Partly cloudy", "good"),
    3: ("Overcast", "mixed"),
    45: ("Fog", "mixed"), 48: ("Freezing fog", "mixed"),
    51: ("Light drizzle", "mixed"), 53: ("Drizzle", "mixed"), 55: ("Heavy drizzle", "wet"),
    56: ("Freezing drizzle", "wet"), 57: ("Freezing drizzle", "wet"),
    61: ("Light rain", "mixed"), 63: ("Rain", "wet"), 65: ("Heavy rain", "wet"),
    66: ("Freezing rain", "wet"), 67: ("Freezing rain", "wet"),
    71: ("Light snow", "snow"), 73: ("Snow", "snow"), 75: ("Heavy snow", "snow"),
    77: ("Snow grains", "snow"),
    80: ("Light showers", "mixed"), 81: ("Showers", "wet"), 82: ("Heavy showers", "wet"),
    85: ("Snow showers", "snow"), 86: ("Heavy snow showers", "snow"),
    95: ("Thunderstorm", "wet"), 96: ("Thunderstorm, hail", "wet"),
    99: ("Thunderstorm, hail", "wet"),
}

DAILY = ("weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_min,"
         "precipitation_sum,precipitation_probability_max,snowfall_sum,"
         "wind_speed_10m_max,wind_gusts_10m_max")

# A 24-hour total is the wrong question. What a traveller needs to know is
# whether it rains while they are OUT - a day with 10 mm that all falls between
# midnight and 8am is a dry day for every purpose that matters. Getting this
# wrong marked a dry, calm ski day as "95% rain, keep indoor options ready".
ACTIVE_FROM, ACTIVE_TO = 8, 18
HOURLY = "precipitation,snowfall,temperature_2m,wind_gusts_10m"


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read())


def forecast(lat, lon, start: dt.date, end: dt.date, tz: str = "auto",
             cache_path: pathlib.Path | None = None):
    """{iso_date: {...}} for each day in range, or {} if unavailable.

    Cached for the day it was fetched - a forecast is worth re-pulling
    tomorrow, and worth reusing an hour from now.
    """
    today = dt.date.today()
    if (start - today).days > HORIZON_DAYS:
        return {}, ("beyond the forecast horizon", False)

    key = f"{lat:.3f},{lon:.3f},{start},{end},{today}"
    cache = {}
    if cache_path and pathlib.Path(cache_path).exists():
        try:
            cache = json.loads(pathlib.Path(cache_path).read_text())
        except Exception:
            cache = {}
    if key in cache:
        return cache[key], ("forecast", True)

    q = urllib.parse.urlencode({
        "latitude": lat, "longitude": lon, "daily": DAILY, "hourly": HOURLY,
        "timezone": tz, "start_date": start.isoformat(), "end_date": end.isoformat(),
    })
    try:
        payload = _get(f"{FORECAST}?{q}")
        d = payload["daily"]
        hourly = payload.get("hourly", {})
    except Exception:
        return {}, ("forecast unavailable", False)

    # Roll the hourly series up into the hours you are actually out in it.
    active = {}
    for i, stamp in enumerate(hourly.get("time", [])):
        day_iso, hour = stamp[:10], int(stamp[11:13])
        a = active.setdefault(day_iso, {"rain": 0.0, "snow": 0.0,
                                        "gust": 0.0, "wet_hours": 0})
        if ACTIVE_FROM <= hour <= ACTIVE_TO:
            mm = hourly["precipitation"][i] or 0.0
            a["rain"] += mm
            a["snow"] += hourly["snowfall"][i] or 0.0
            a["gust"] = max(a["gust"], hourly.get("wind_gusts_10m", [0] * (i + 1))[i] or 0.0)
            if mm >= 0.2:
                a["wet_hours"] += 1

    out = {}
    for i, day in enumerate(d["time"]):
        code = d["weather_code"][i]
        desc, band = WMO.get(code, ("Unknown", "mixed"))
        rain_24h = d["precipitation_sum"][i] or 0.0
        snow_24h = d["snowfall_sum"][i] or 0.0
        prob = d["precipitation_probability_max"][i] or 0
        act = active.get(day, {})
        # Judge the day on its active hours; keep the 24h figure for context.
        rain = act.get("rain", rain_24h)
        snow = act.get("snow", snow_24h)
        wet_hours = act.get("wet_hours", 0)

        # Escalate on volume, not just on the code: a "showers" code with 30 mm
        # behind it is not a showers day.
        # Exhaustive on purpose. An earlier version left a gap where a day
        # with exactly 0.5 mm matched no branch and silently kept the WMO
        # code's own verdict - so a dry ski day stayed labelled "wet" because
        # it had rained overnight.
        if snow > 0.5:
            band = "snow"
        elif rain >= 12:
            band = "wet"
        elif rain >= 2.5 or wet_hours >= 3:
            band = "mixed"
        else:
            band = "good"

        out[day] = {
            "code": code, "description": desc, "band": band,
            "rain_24h_mm": round(rain_24h, 1), "snow_24h_cm": round(snow_24h, 2),
            "wet_hours": wet_hours,
            "active_window": f"{ACTIVE_FROM:02d}:00-{ACTIVE_TO:02d}:00",
            "temp_max": d["temperature_2m_max"][i],
            "temp_min": d["temperature_2m_min"][i],
            "feels_like_min": d["apparent_temperature_min"][i],
            "rain_mm": round(rain, 1), "snow_cm": round(snow, 2),
            "rain_chance": prob,
            "wind_kmh": d["wind_speed_10m_max"][i],
            "gust_kmh": d["wind_gusts_10m_max"][i],
            "outdoor_ok": band in ("good", "mixed"),
            "summary": _summary(desc, d["temperature_2m_min"][i],
                                d["temperature_2m_max"][i], rain, snow, prob),
        }

    if cache_path:
        cache[key] = out
        pathlib.Path(cache_path).write_text(json.dumps(cache, indent=1))
    return out, ("forecast", True)


def _summary(desc, tmin, tmax, rain, snow, prob):
    bits = [f"{desc}, {tmin:.0f} to {tmax:.0f}°C"]
    if snow > 0.05:
        bits.append(f"{snow:.1f} cm snow while you are out")
    if rain > 0.05:
        bits.append(f"{rain:.1f} mm rain between 08:00 and 18:00")
    else:
        bits.append("dry between 08:00 and 18:00")
    return ", ".join(bits)


def advice(day: dict) -> list[str]:
    """Plain warnings a traveller can act on."""
    out = []
    b = day["band"]
    if b == "snow":
        out.append(f"Snow forecast ({day['snow_cm']:.1f} cm). Mountain roads may need "
                   f"chains; check road status before driving anywhere high.")
    if day.get("note_24h"):
        out.append(day["note_24h"].capitalize() + ".")
    if day["rain_mm"] >= 20:
        out.append(f"{day['rain_mm']:.0f} mm of rain during the hours you are out - "
                   f"this is a day to have indoor options ready, not a day to hope.")
    elif b == "wet":
        out.append(f"{day['rain_mm']:.0f} mm expected while you are out - keep the "
                   f"indoor alternates handy.")
    if day["feels_like_min"] is not None and day["feels_like_min"] <= 0:
        out.append(f"Feels like {day['feels_like_min']:.0f}°C at its coldest - "
                   f"that is gloves and a hat, not just a jacket.")
    if day["gust_kmh"] and day["gust_kmh"] >= 60:
        out.append(f"Gusts to {day['gust_kmh']:.0f} km/h - gondolas and scenic flights "
                   f"stop running in wind like that.")
    return out
