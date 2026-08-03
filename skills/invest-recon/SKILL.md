---
name: invest-recon
description: "Passive investing recon for moomoo AU. Daily info-only market pulse and Saturday decision review (buy/watch/sell with thesis + invalidation). Credible sources only, fee-aware at small portfolio size, discipline gates on every call, monthly call postmortems, logs executed trades to trading-journal. Modes: daily, weekly, trade, doctor."
metadata:
  hermes:
    category: productivity
---

# invest-recon

**Trigger**: `/invest-recon [daily|weekly|trade ...|doctor]` or "/invest", "run invest recon", "market pulse", "portfolio review"
**Domain**: productivity (finance)
**Automation**: remote via Hermes cron — daily pulse 07:30 Australia/Sydney Mon–Fri (just after US close), weekly review Saturday 09:00. Delivers TL;DR to Telegram when a channel exists.

## Description

Investing recon for an Australia-based operator trading globally through moomoo AU.
The operator executes all trades manually; this skill only produces information and
ranked recommendations. Companion skill: `trading-journal` (P&L log lives there).

Design intent, in priority order: **passive** (minimal trades, minimal screen time),
**fee-aware** (small portfolio — costs dominate), **grounded** (credible sources only),
**decision-quality over frequency** (the default weekly outcome is "no action").

Discipline gate, sizing, cooldown, and postmortem rules adapted from
tradermonty/claude-trading-skills (MIT) — simplified to inline rules for a passive
small portfolio; no Python artifacts.

## Strategy contract (current)

Read `portfolio.json` (below) for live values; these are the standing rules:

- **Core + satellite.** Core ≈75% of capital in one broad, low-fee, US-listed global
  or S&P 500 ETF — buy and hold, never traded on signals. Satellite ≈25% for
  conviction positions the weekly review generates.
- **Universe**: global, but default to US-listed instruments. ASX individual shares
  are effectively excluded below ~$500/position by the ASX minimum marketable
  parcel rule — recheck this constraint when the portfolio grows past ~$2k.
- **Trade budget**: max 2 trades/month by default. A week with no trade call is a
  successful week, say so plainly.
- **Every buy call must state**: thesis (one paragraph), size in AUD, invalidation
  (the specific observable event/level that kills the thesis), and time horizon.
  No invalidation = not a call.
- **Sell calls only on thesis break or better use of capital** — never on price
  noise. Core is never a sell candidate on signals.
- **Fee gate**: before any call, estimate round-trip cost (commission both ways +
  FX conversion both ways + spread) as % of position. If required edge to break
  even exceeds ~2%, the position is too small or the idea too weak — say which.
  Verify moomoo AU's current fee schedule when computing (fees change; do not
  hardcode). Known structure to check: US trade commission, AUD↔USD FX rate
  markup, ASX commission, US fractional-share availability.

## Position sizing

Size from risk, not conviction: **loss-at-invalidation ≤ 5% of total portfolio
value**. `size = (0.05 × portfolio_value) / invalidation_distance_pct`, capped at
the satellite allocation. Use fractional shares; **floor, never round up**. Show
the math in the digest: "at $X, invalidation at $Y (−Z%), size $N → max loss $M
(_% of portfolio)". Survival first: a 50% loss needs a 100% gain to recover.

## Pre-trade gate — every Buy/Sell call gets a GO / NO-GO line

A call only appears as **Recommended** if all pass; otherwise it appears in Watch
with the failed gate named. Print the gate result with each call.

1. **Plan written**: thesis + invalidation + horizon + sources all present.
2. **Sized by rule**: sizing math above applied; max loss ≤ 5% of portfolio.
3. **Fee gate** passes (< 2% round trip).
4. **Cooldown** (revenge-trade guard): no satellite position closed at a loss in
   the last 30 days. If one was, new satellite buys are NO-GO this cycle —
   existing positions and core DCA are unaffected.
5. **Circuit breaker**: if realized satellite losses over the trailing 3 months
   exceed 15% of portfolio value, satellite is frozen until the next monthly
   review explicitly lifts it; core contributions continue. Prevents escalation
   after damage, does not force liquidation.
6. **Trade budget** not exhausted (2/month).

## Bear case requirement

Every Buy call must include the strongest sourced argument **against** the
position and one line on why the thesis survives it. If that line cannot be
written honestly, demote the call to Watch. One model convincing itself is the
failure mode this exists to catch.

## State

`/root/agentic-workspace/domains/productivity/trading/portfolio.json`:
holdings (ticker, units, cost basis, currency, thesis, invalidation), cash by
currency, watchlist (ticker, thesis, trigger-to-buy, invalidation, date added,
source links), **calls ledger** (`calls[]`: date, type buy/sell/watch, ticker,
price_at_call, invalidation, gate_result, taken true/false, outcome — outcome
stays null until scored by a postmortem), `seen` story-dedupe list (21-day
window), settings (trade budget, core/satellite split, risk limits). Update on
every `trade` command; prune `seen` entries older than 21 days on every run.

## Output location (resolve first)

Same resolution order as insights-recon:
1. `$AGENTIC_VAULT` / `$CLAUDE_VAULT` env var.
2. Known paths: `/opt/agentic/obsidian/vault` (VPS), `~/Documents/ajqcd-zaozt`.
3. `vaultPath` in `server/data/user-config.json` of an agentic-workspace checkout.

Digest path: `<vault>/Agentic Output/invest/<date>.md` (weekly review:
`<date>-weekly.md`). If no vault resolves, print the digest instead. Never guess
a path. Announce the vault path in chat when writing.

## Sources — credible only, this is a hard rule

Rank: primary > official data > quality press > market data. Cite every claim
that feeds a recommendation with a link. If a claim can't be traced to this pool,
it does not enter the digest.

- **Primary**: company filings and investor-relations releases (SEC EDGAR, ASX
  announcements), central banks (RBA, US Fed/FOMC), official stats (ABS, BLS).
- **Official market data**: index levels, prices, AUDUSD — Yahoo Finance quote
  endpoints or equivalent free API via curl/WebFetch; never quote a price from a
  news article when a data source is available.
- **Quality press** (via WebSearch/WebFetch): Reuters, AFR, Bloomberg, FT, WSJ,
  Morningstar. Attribute the outlet.

**Excluded by choice, not oversight**: Reddit, X, TikTok, YouTube, Polymarket,
and the `last30days` skill — the operator chose a curated credible pool over
engagement volume; social sentiment is exactly the "ungrounded speculation" this
skill exists to filter out. Do not re-pitch these sources. **Do** note in the
weekly Gaps line if the credible pool demonstrably missed a story that mattered —
that is evidence, not a proposal.

Analyst price targets and "X upgrades Y" items are press tier at best: report who
said it, never treat it as a thesis by itself.

## Modes

### `/invest-recon daily` — information only, no trade calls

~07:30 Sydney, after US close. Digest sections:

1. **Action line** (always first): almost always
   `No action needed today.` — or, rarely, `⚡ CHECK: <one line>` (gate below).
2. **Markets**: S&P 500, Nasdaq, ASX 200, AUDUSD, US 10-yr — close and 1-day move.
   One line each, numbers from a data source.
3. **Holdings check**: each holding vs its invalidation level/event. One line each.
4. **Watchlist check**: any trigger-to-buy hit or approached? State it; the
   decision still waits for Saturday unless the urgent gate fires.
5. **TL;DR**: 3–5 bullets, the market day in one line each, only stories relevant
   to holdings, watchlist, or macro (rates, AUD).
6. **Source health**: failed fetches, or "all green".

**Urgent gate** (keep rare or it becomes noise): fires only for (a) material
company-specific news on a **holding** (earnings surprise, guidance cut, M&A,
fraud/regulatory action), or (b) a watchlist trigger hit where waiting until
Saturday plausibly costs the entry. Requires a one-line honest justification.
Market-wide drops are NOT urgent for a passive holder — note them, hold the line.
Under Hermes cron, an urgent day's Telegram message opens with `⚡` and the item.

### `/invest-recon weekly` — the decision review (Saturday)

All markets closed; nothing can be traded impulsively. Sections:

1. **Action line**: `Recommended: <1–2 specific actions>` or `No action this week.`
2. **Portfolio**: value in AUD, week/all-time change, vs benchmark (VT or S&P 500
   in AUD terms). Honest, no spin.
3. **Buy / Watch / Sell** — each entry with thesis, size (show sizing math), bear
   case, invalidation, horizon, sources, and its **pre-trade gate GO/NO-GO line**.
   Watch = add to watchlist with a concrete trigger-to-buy. Empty sections stay
   present with "none".
4. **Fee check**: round-trip cost math for any Buy/Sell call.
5. **Watchlist hygiene**: drop entries whose thesis expired; say why.
6. **Gaps** (one line, optional): what the source pool missed this week, if anything.
7. **Learnings**: append notable ones to
   `domains/productivity/trading/learnings.md`.

Record every Buy/Sell/Watch call in the `calls[]` ledger with the price at call
time — including NO-GO and Watch calls, so postmortems can score the road not
taken.

First Saturday of the month: add a **Monthly** section — performance table,
whether the strategy contract still fits the capital size, the **call
postmortem** (below), circuit-breaker status (lift or hold a satellite freeze,
with reasoning), and one paragraph of self-critique. Cross-check against
`trading-journal`'s journal for pattern flags.

**Call postmortem** (monthly): score every ledger call ≥20 trading days old and
not yet scored, against current price and its invalidation:
- `TRUE_POSITIVE` — call direction matched what happened
- `FALSE_POSITIVE` — taken call went against us / hit invalidation
- `MISSED_OPPORTUNITY` — Watch or NO-GO call that would have worked
- `REGIME_MISMATCH` — right idea, market-wide move overwhelmed it
Report the running hit rate honestly. If false positives cluster (3+ in a
quarter sharing a reasoning pattern), name the pattern in `learnings.md` and
tighten the corresponding gate. Honest attribution is the point: the ledger
exists so the skill's advice is auditable, not just the trades.

### `/invest-recon trade <details>` — log an executed trade

E.g. `/invest-recon trade bought 0.3 VOO @ 512.40 USD` or free text. Steps:
1. Update `portfolio.json` (holdings, cash, cost basis; new positions need
   thesis + invalidation — pull from the call that recommended it, or ask).
   Mark the matching `calls[]` entry `taken: true`. If a position was closed at
   a loss, note the date — it starts the 30-day cooldown.
2. Append the trade to `domains/productivity/trading/journal.md` in
   trading-journal's format.
3. Confirm back: position, new cash balance, the invalidation now being watched,
   and remaining trade budget for the month.

### `/invest-recon doctor`

Fetch one item from each source tier, report reachable/broken, and verify
portfolio.json parses and vault path resolves.

## Boundaries

- Never execute, queue, or automate trades. The operator trades in moomoo.
- Never state certainty about future prices. Recommendations are ranked analysis
  with visible reasoning and sources; the operator takes the risk.
- General information, not personal financial advice; does not consider tax
  positions beyond flagging when a sale would realize a gain/loss worth checking.
- Vault writes only under `Agentic Output/invest/`. State writes only under
  `domains/productivity/trading/`.
- Changing the source pool, strategy contract, gate rules, or risk limits: only
  at a weekly/monthly review with the reasoning logged in `learnings.md`.
