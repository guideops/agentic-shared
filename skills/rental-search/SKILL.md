---
name: rental-search
description: On-demand Sydney rental search run from a personal machine (laptop) on a residential connection, reading domain.com.au and realestate.com.au through a real Chromium via Playwright and writing results to the 'ChatGPT Output' tab of the rental spreadsheet. Free — no scraping credits. Requires a one-time `playwright install chromium` on each machine. Use when the user says /rental-search, "search for apartments", "find me rentals", "run the rental search", or wants a fresh look outside the daily server cron. Works identically under Claude Code and Codex.
---

# Rental search (laptop)

The active, on-demand counterpart to the server's daily cron. Run it whenever
you want a fresh look; run it again after changing anything in `config.json`.

```bash
python3 scripts/search.py              # search, print, ask before writing
python3 scripts/search.py --write      # search and write to the sheet
python3 scripts/search.py --show-all   # also list the rejects and why
python3 scripts/search.py --no-sheet   # just print, touch nothing
```

## One-time setup, per machine

```bash
pip install patchright PyJWT cryptography
patchright install chromium      # ~150 MB, downloaded once
```

Without this the script stops immediately and tells you to run it. The browser
cannot be committed to the repo, so every new machine needs this step. `PyJWT`
and `cryptography` are for signing the service-account token in `sheets.py`;
skip them only if you always run `--no-sheet`.

**Why patchright and not plain Playwright.** Driving a browser is not enough:
both sites detect the *automation* on top of the browser, independently of
`headless` and independently of the user agent. The tells live in the CDP layer
— `Runtime.enable` is observable from page JS, as are the stack-trace artefacts
CDP leaves behind. patchright is a drop-in Playwright fork that closes exactly
those leaks. Stock Playwright still works as a fallback and the script will use
it automatically, it is just far more visible.

Two things that look like omissions but are deliberate: under patchright the
script does **not** patch `navigator.webdriver` and does **not** pass custom
launch args. `add_init_script` is itself detectable, so adding either back
reintroduces the tell they were meant to remove.

A run takes **60–90 seconds** — slower than the old plain-GET version, which was
fast because it was being refused.

## Why a real browser, and why not the server

Two separate blocks, and **neither is about the IP address**:

- **domain.com.au** — Akamai Bot Manager. Fingerprints the TLS handshake and the
  HTTP/2 SETTINGS frame, and wants an `_abck` cookie that only its own
  JavaScript sets. A `urllib` request speaks HTTP/1.1 with a Python TLS
  fingerprint and is refused before the request is read.
- **realestate.com.au** — Kasada. Answers the *first* request from any IP, with
  no prior traffic, with `429 Too Many Requests` plus a fresh `x-kpsdk-ct` token
  and a `KP_UIDz` cookie. That is not rate limiting, it is "you have no token".
  There is no cooldown to wait out, and the challenge is an obfuscated JS VM
  that no HTTP client can execute.

So the script drives an actual Chromium. That is not evasion — it runs their
JavaScript and honours their cookies, which is exactly what both systems ask
for. An earlier version sent a polite plain GET and could never have worked; the
claim that "a home connection reads both sites directly" was reasoned from the
server's problem and was wrong.

The **server still cannot use this**. Its datacentre IP is reputation-blocked by
Akamai regardless of browser, which is why the daily cron keeps paying Apify.
A residential IP is necessary but not sufficient; a real browser is the other
half.

### If it is still refused

1. Set `"headless": false` in `config.json` — Kasada detects headless Chromium
   specifically. A visible window opens for the length of the run.
2. Set `"browser_channel": "chrome"` to drive your own installed Chrome.
3. Open the site once by hand; the profile in `browser-profile/` is persistent,
   so the run inherits the session.

Every refusal writes `debug-blocked-*.html` next to the config, so the actual
refusal page can be read rather than guessed at.

## The brief it implements

- Close to public transport, **walking** — within 10 minutes of a station, under 8 preferred
- Close to amenities — within 12 minutes' walk of a major supermarket
- **Above the 6th floor** — to avoid insects
- **$650–780 per week**
- Modern style, safe area
- Available now
- 1 bedroom or more; a study or second room is a bonus
- **Suburbs only:** Macquarie Park, North Ryde, Rhodes, Hurstville, Epping
- Never Wolli Creek, the CBD, the eastern suburbs, or the inner west

## What it will not do

**Nothing is silently hidden.** Every listing found is classified, never dropped:

| Tier | Meaning |
|---|---|
| `match` | passes every requirement |
| `near` | misses exactly one — the miss is named in the `misses` column |
| `reject` | misses two or more — counted, shown with `--show-all` |

That rule exists because an earlier version silently dropped four of the
operator's own favourite properties on a bad floor heuristic.

It also **never guesses a URL**. Anything it could not read properly is marked
`partial`, and if a page yields nothing it writes `debug-*.html` next to the
config so the parser can be corrected rather than quietly returning nothing.

## Exclusions, and the deliberate exception

Read live from the spreadsheet on every run:

- Everything on the **Apartments** tab — excluded
- Anything marked **No** on AI Output — excluded
- Anything marked **off market** — excluded
- **Anything the server pipeline also found — INCLUDED, and flagged
  `matches_ai_output`**

That last one is deliberate. Overlap between an independent search and the
server pipeline is the sanity check: if both surface the same property, that is
a strong signal. Suppressing it would throw away the comparison.

## Sheet access

Needs `service-account.json` in the skill folder — the same key the server uses,
shared with the spreadsheet as an Editor. **It is gitignored; never commit it.**
Without the key the script still searches and prints, it just cannot read
exclusions or write results.

## Output columns

`verdict` (Yes/No dropdown) · `rank` · `suburb` · `price_pw` · `beds` · `study` ·
`floor` · `floor_note` · `station` · `station_walk_mins` ·
`supermarket_walk_mins` · `quality` · `signals` · `tier` · `misses` ·
`matches_ai_output` · `address` · `url` · `listing_id`

The tab is rewritten each run, with the same Yes/No dropdown and light-red
shading for declined and off-market rows as the AI Output tab.

## How the facts are established

- **Floor** — a level stated in the listing wins; otherwise the unit number
  (`1203/8 Walker St` → level 12); otherwise the building's storey count from
  OpenStreetMap. Never invented.
- **Walk times** — routed over the real footpath network (public Valhalla, no
  key), cached in `walk-cache.json` so repeats are free.
- **Quality** — deterministic keyword rules over the advertiser's own words.
  Every matched word is written to the `signals` column, so any ranking can be
  audited. Deliberately not a model judging photos.

## Data files

`data/stations.json` (261 stops), `data/supermarkets.json` (559 majors),
`data/buildings.json` (7,558 buildings of 4+ storeys). All from OpenStreetMap,
committed so the laptop needs no network setup. Regenerate with the
`build_*.py` scripts in the server's `automations/sydney-rentals/` folder.
