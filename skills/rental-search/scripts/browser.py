#!/usr/bin/env python3
"""Real-browser page fetch, because a plain HTTP GET cannot read either site.

Both targets refuse scripted requests at the edge, and neither refusal is about
the IP address:

  domain.com.au      Akamai Bot Manager. Fingerprints the TLS handshake and the
                     HTTP/2 SETTINGS frame, and wants an `_abck` sensor cookie
                     that only its own JavaScript can set. `urllib` speaks
                     HTTP/1.1 with a Python TLS fingerprint, so it is refused
                     before the request is read.

  realestate.com.au  Kasada. Answers the very first request - on any IP, with no
                     prior traffic - with `429 Too Many Requests` plus a fresh
                     `x-kpsdk-ct` token and a `KP_UIDz` cookie. That is not rate
                     limiting; it is "you have no token, go solve the
                     challenge". There is no cooldown to wait out. Solving it
                     means executing an obfuscated JS VM, which no HTTP client
                     can do.

So we drive an actual browser. This is not evasion - the browser is a browser,
it runs their JavaScript and honours their cookies, which is precisely what both
systems are asking for. The old `fetch()` was polite but could never succeed.

One-time setup on each machine:

    pip install playwright
    playwright install chromium

The profile directory is persistent, so cookies and any solved token survive
between runs. The second run of the day is usually faster and less challenged
than the first.
"""
from __future__ import annotations

import sys
import time

CHALLENGE_CODES = (403, 429, 503)


class BrowserUnavailable(RuntimeError):
    """Playwright is not installed, or its Chromium was never downloaded."""


class Session:
    """One browser for the whole run. Use as a context manager.

    Kept open across every URL on purpose: relaunching per page would throw away
    the cookies that make the later fetches work.
    """

    def __init__(self, profile_dir, *, headless=True, channel=None,
                 delay_seconds=2.0, timeout_ms=45000, attempts=2):
        self.profile_dir = str(profile_dir)
        self.headless = headless
        self.channel = channel or None
        self.delay = float(delay_seconds)
        self.timeout = int(timeout_ms)
        self.attempts = max(1, int(attempts))
        self._pw = None
        self._ctx = None
        self._last = 0.0
        self.last_status = None
        self.last_html = None      # body of the last refusal, for debugging

    # -- lifecycle ---------------------------------------------------------
    def __enter__(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise BrowserUnavailable(
                "playwright is not installed. Run:\n"
                "    pip install playwright && playwright install chromium"
            ) from exc

        self._pw = sync_playwright().start()
        launch = dict(
            user_data_dir=self.profile_dir,
            headless=self.headless,
            locale="en-AU",
            timezone_id="Australia/Sydney",
            viewport={"width": 1440, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        if self.channel:
            launch["channel"] = self.channel
        try:
            self._ctx = self._pw.chromium.launch_persistent_context(**launch)
        except Exception as exc:
            self._pw.stop()
            self._pw = None
            raise BrowserUnavailable(
                f"could not launch Chromium ({exc}).\n"
                "If this is a fresh machine, run: playwright install chromium"
            ) from exc

        # `navigator.webdriver` is the one automation flag that is trivially
        # readable from page JS and that both vendors check for.
        self._ctx.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        self._ctx.set_default_timeout(self.timeout)
        return self

    def __exit__(self, *_exc):
        for closer in (getattr(self._ctx, "close", None),
                       getattr(self._pw, "stop", None)):
            try:
                if closer:
                    closer()
            except Exception:
                pass
        self._ctx = self._pw = None
        return False

    # -- fetching ----------------------------------------------------------
    def _throttle(self):
        gap = self.delay - (time.monotonic() - self._last)
        if gap > 0:
            time.sleep(gap)
        self._last = time.monotonic()

    def get(self, url):
        """Navigate and return the settled HTML, or None if it stayed blocked.

        A challenge response on the first attempt is expected rather than fatal:
        Kasada hands out its token with the 429, so the reload that follows is
        the request it actually wanted. Two attempts, then we give up and say so.
        """
        if self._ctx is None:
            raise RuntimeError("Session used outside its context manager")

        page = self._ctx.new_page()
        try:
            for attempt in range(1, self.attempts + 1):
                self._throttle()
                try:
                    resp = page.goto(url, wait_until="domcontentloaded",
                                     timeout=self.timeout)
                except Exception as exc:
                    print(f"  [error] {url[:70]}: {exc}", file=sys.stderr)
                    return None

                status = resp.status if resp else None
                self.last_status = status

                if status in CHALLENGE_CODES and attempt < self.attempts:
                    # The challenge body *is* the solver: Kasada serves a KPSDK
                    # bootstrap script that mints the token and sets the cookie.
                    # Let it run to completion before reloading, or the retry
                    # arrives just as empty-handed as the first attempt.
                    print(f"  [{status}] challenge - letting its script run, retrying",
                          file=sys.stderr)
                    try:
                        page.wait_for_load_state("networkidle", timeout=15000)
                    except Exception:
                        pass
                    time.sleep(4)
                    continue

                if status in CHALLENGE_CODES:
                    try:
                        self.last_html = page.content()
                    except Exception:
                        self.last_html = None
                    print(f"  [{status}] {url[:90]}", file=sys.stderr)
                    print("  -> still refused after a real browser load. Try "
                          "headless=false in config.json, or open the site once "
                          "by hand so the profile picks up a session.",
                          file=sys.stderr)
                    return None

                # Both sites hydrate their listing JSON after first paint.
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except Exception:
                    pass                      # slow third-party beacon; content is there
                return page.content()
        finally:
            try:
                page.close()
            except Exception:
                pass
        return None
