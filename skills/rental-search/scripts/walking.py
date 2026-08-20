#!/usr/bin/env python3
"""Real pedestrian walking times, cached.

Straight-line distance systematically understates a walk — buildings, rivers and
one-way stair access all get ignored. This routes over the actual footpath
network via the public FOSSGIS Valhalla instance (no API key), and falls back to
a calibrated straight-line estimate if that service is unreachable, so a routing
outage degrades the numbers instead of killing the run.

Every answer is cached on disk by rounded coordinate pair, so the same
property/station pair is only ever routed once.
"""
from __future__ import annotations

import json
import math
import pathlib
import time
import urllib.request

VALHALLA = "https://valhalla1.openstreetmap.de/route"
UA = {"User-Agent": "sydney-rentals/1.0 (personal rental search)",
      "Content-Type": "application/json"}

# Measured against Valhalla on a known CBD leg: 0.86 km routed = 10.8 min,
# i.e. ~80 m/min on the real network. Straight-line needs a detour factor on top.
METRES_PER_MIN = 80.0
DETOUR = 1.30

_MIN_GAP_S = 0.6          # be a polite citizen of a free public service
_last_call = [0.0]


class WalkCache:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.data = json.loads(path.read_text()) if path.exists() else {}
        self.dirty = False
        self.routed = 0
        self.estimated = 0

    @staticmethod
    def _key(a, b):
        return f"{a[0]:.5f},{a[1]:.5f}>{b[0]:.5f},{b[1]:.5f}"

    def save(self):
        if self.dirty:
            self.path.write_text(json.dumps(self.data))
            self.dirty = False

    def minutes(self, a, b, allow_network=True):
        """Walking minutes from (lat,lon) a to b. Returns (mins, how)."""
        k = self._key(a, b)
        hit = self.data.get(k)
        if hit is not None:
            return hit["m"], hit["how"]

        mins, how = None, "estimated"
        if allow_network:
            mins = self._route(a, b)
            if mins is not None:
                how = "routed"
                self.routed += 1
        if mins is None:
            mins = haversine_m(*a, *b) * DETOUR / METRES_PER_MIN
            self.estimated += 1

        mins = round(mins, 1)
        self.data[k] = {"m": mins, "how": how}
        self.dirty = True
        return mins, how

    def _route(self, a, b):
        gap = _MIN_GAP_S - (time.monotonic() - _last_call[0])
        if gap > 0:
            time.sleep(gap)
        _last_call[0] = time.monotonic()
        body = {"locations": [{"lat": a[0], "lon": a[1]}, {"lat": b[0], "lon": b[1]}],
                "costing": "pedestrian", "units": "km"}
        try:
            req = urllib.request.Request(VALHALLA, data=json.dumps(body).encode(),
                                         headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                d = json.loads(r.read())
            return d["trip"]["summary"]["time"] / 60.0
        except Exception:
            return None


def haversine_m(lat1, lon1, lat2, lon2):
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(x))


def nearest(point, places, limit=6):
    """The `limit` closest places by straight line - a cheap shortlist to route."""
    scored = sorted(places, key=lambda p: haversine_m(point[0], point[1],
                                                      p["lat"], p["lon"]))
    return scored[:limit]


def best_walk(point, places, cache, limit=4):
    """Route to the few nearest candidates and return the shortest actual walk.

    The straight-line nearest is often not the shortest walk - a station across
    a rail cutting or a motorway can be 200 m away and a 15 minute detour.
    """
    best = (None, None, None)
    for p in nearest(point, places, limit):
        mins, how = cache.minutes(point, (p["lat"], p["lon"]))
        if best[1] is None or mins < best[1]:
            best = (p, mins, how)
    return best
