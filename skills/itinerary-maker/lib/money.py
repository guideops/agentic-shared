#!/usr/bin/env python3
"""Turn the price strings people actually write into numbers you can add up.

Sources state prices as "Adult $205, child $155", "from US$59.50", "$85-120 per
adult", "free", or nothing at all. This pulls a per-adult range out of that mess
and says how confident it is, so a spreadsheet can total a day without
pretending a 2017 Wikivoyage figure is a quote.

Nothing here invents a number. A string with no price in it returns None, and
the renderers print "no price found" rather than a zero that would silently
flatter the total.
"""
from __future__ import annotations

import re

# Rough conversions to NZD. Stated openly rather than hidden, because they age.
# Update RATES and RATES_AS_OF together.
RATES = {"NZD": 1.0, "USD": 1.65, "AUD": 1.09, "EUR": 1.78, "GBP": 2.10}
RATES_AS_OF = "August 2026, indicative only"

FREE = re.compile(r"\b(free|no charge|gratis|donation)\b", re.I)
CURRENCY = re.compile(r"\b(NZ\$|US\$|AU\$|NZD|USD|AUD|EUR|GBP|£|€)", re.I)
# A number only counts as money when a currency symbol is attached to it.
# Without that anchor "6 luge rides" became $6, "13 Jun to 4 Oct 2026" became a
# $4-$2026 range, and every price string containing a year was ruined.
AMOUNT = re.compile(
    r"(?:NZ\$|US\$|AU\$|\$|£|€)\s*(\d{1,4}(?:\.\d{1,2})?)"
    r"(?:\s*(?:-|–|to)\s*\$?\s*(\d{1,4}(?:\.\d{1,2})?))?", re.I)
YEAR = re.compile(r"\b(19|20)\d{2}\b")
ADULT_HINT = re.compile(r"\badult\b", re.I)
CHILD_HINT = re.compile(r"\b(child|youth|kid|student|senior)\b", re.I)
UNVERIFIED = re.compile(r"\b(unverified|check current|verify|tbc|varies)\b", re.I)


def _currency(text: str) -> str:
    m = CURRENCY.search(text or "")
    if not m:
        return "NZD"
    tok = m.group(1).upper().replace("$", "")
    return {"NZ": "NZD", "US": "USD", "AU": "AUD", "£": "GBP", "€": "EUR",
            "GBP": "GBP", "EUR": "EUR", "NZD": "NZD", "USD": "USD",
            "AUD": "AUD"}.get(tok, "NZD")


def parse(text: str, kind: str = ""):
    """-> {'low','high','currency','nzd_low','nzd_high','confidence','display'} or None."""
    if not text or not str(text).strip():
        return None
    t = str(text).strip()

    if FREE.search(t) and not AMOUNT.search(t):
        return {"low": 0.0, "high": 0.0, "currency": "NZD", "nzd_low": 0.0,
                "nzd_high": 0.0, "confidence": "high", "display": "free"}

    # Prefer the adult figure when the string breaks the price out by person.
    scope = t
    if ADULT_HINT.search(t) and CHILD_HINT.search(t):
        head = re.split(CHILD_HINT, t)[0]
        if AMOUNT.search(head):
            scope = head

    scope = YEAR.sub(" ", scope)          # a year is never a price
    nums = []
    for m in AMOUNT.finditer(scope):
        nums.append(float(m.group(1)))
        if m.group(2):
            nums.append(float(m.group(2)))
    nums = [n for n in nums if 0 < n <= 5000]
    if not nums:
        return None

    low, high = min(nums), max(nums)
    # A single figure introduced by "from" is a floor, not a quote.
    if len(nums) == 1 and re.search(r"\bfrom\b", t, re.I):
        high = low * 1.6

    cur = _currency(t)
    rate = RATES.get(cur, 1.0)
    conf = "low" if UNVERIFIED.search(t) else ("medium" if len(nums) > 1 else "medium")

    return {"low": round(low, 2), "high": round(high, 2), "currency": cur,
            "nzd_low": round(low * rate, 2), "nzd_high": round(high * rate, 2),
            "confidence": conf, "display": t}


def nzd_range(entries) -> tuple[float, float, int, int]:
    """Total a list of parsed prices. -> (low, high, counted, unpriced)."""
    lo = hi = 0.0
    counted = unpriced = 0
    for e in entries:
        if not e:
            unpriced += 1
            continue
        lo += e["nzd_low"]
        hi += e["nzd_high"]
        counted += 1
    return round(lo, 2), round(hi, 2), counted, unpriced


def fmt(lo: float, hi: float) -> str:
    if lo == hi == 0:
        return "free"
    if abs(hi - lo) < 0.5:
        return f"NZ${lo:,.0f}"
    return f"NZ${lo:,.0f}-{hi:,.0f}"
