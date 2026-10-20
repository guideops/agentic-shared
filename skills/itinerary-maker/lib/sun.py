#!/usr/bin/env python3
"""Sunrise and sunset, computed rather than looked up.

An itinerary that puts a scenic lookout after dark is worse than useless, and
in late winter at 45 degrees south the usable day is barely nine hours. This is
the NOAA solar position algorithm - no API, no key, no network, accurate to
about a minute, which is far inside the tolerance of a travel plan.
"""
from __future__ import annotations

import datetime as dt
import math

ZENITH = 90.833          # standard refraction-corrected sunrise/sunset zenith


def _julian_day(date: dt.date) -> float:
    y, m, d = date.year, date.month, date.day
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5


def _solar_event(lat, lon, date, utc_offset_h, rising: bool):
    jd = _julian_day(date)
    t = (jd - 2451545.0) / 36525.0

    geom_mean_long = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360
    geom_mean_anom = 357.52911 + t * (35999.05029 - 0.0001537 * t)
    eccent = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)

    m_rad = math.radians(geom_mean_anom)
    sun_eq = (math.sin(m_rad) * (1.914602 - t * (0.004817 + 0.000014 * t))
              + math.sin(2 * m_rad) * (0.019993 - 0.000101 * t)
              + math.sin(3 * m_rad) * 0.000289)
    true_long = geom_mean_long + sun_eq
    app_long = true_long - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * t))

    obliq = (23 + (26 + ((21.448 - t * (46.815 + t * (0.00059 - t * 0.001813)))) / 60) / 60)
    obliq_corr = obliq + 0.00256 * math.cos(math.radians(125.04 - 1934.136 * t))

    decl = math.degrees(math.asin(
        math.sin(math.radians(obliq_corr)) * math.sin(math.radians(app_long))))

    vary = math.tan(math.radians(obliq_corr / 2)) ** 2
    eq_time = 4 * math.degrees(
        vary * math.sin(2 * math.radians(geom_mean_long))
        - 2 * eccent * math.sin(m_rad)
        + 4 * eccent * vary * math.sin(m_rad) * math.cos(2 * math.radians(geom_mean_long))
        - 0.5 * vary * vary * math.sin(4 * math.radians(geom_mean_long))
        - 1.25 * eccent * eccent * math.sin(2 * m_rad))

    cos_ha = (math.cos(math.radians(ZENITH))
              / (math.cos(math.radians(lat)) * math.cos(math.radians(decl)))
              - math.tan(math.radians(lat)) * math.tan(math.radians(decl)))
    if cos_ha > 1:
        return None          # polar night - the sun never rises
    if cos_ha < -1:
        return None          # midnight sun - it never sets
    ha = math.degrees(math.acos(cos_ha))
    if not rising:
        ha = -ha

    minutes = 720 - 4 * (lon + ha) - eq_time + utc_offset_h * 60
    return minutes % 1440


def sun_times(lat: float, lon: float, date: dt.date, utc_offset_h: float):
    """(sunrise_min, sunset_min) as minutes after local midnight.

    Either may be None at extreme latitudes, where the caller must fall back to
    a fixed working day rather than pretending there is a sunset.
    """
    return (_solar_event(lat, lon, date, utc_offset_h, True),
            _solar_event(lat, lon, date, utc_offset_h, False))


def hhmm(minutes) -> str:
    if minutes is None:
        return "--:--"
    minutes = int(round(minutes))
    return f"{(minutes // 60) % 24:02d}:{minutes % 60:02d}"
