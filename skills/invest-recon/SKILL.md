---
name: invest-recon
description: "Passive investing recon for moomoo AU. Daily info-only market pulse and Saturday decision review (buy/watch/sell with thesis + invalidation). On-demand single-stock dossiers (deep) and supply-chain/picks-and-shovels mapping (chain), all jargon translated to plain English so the operator learns while deciding. Gamble sleeve for labeled speculative bets. Credible sources only, fee-aware at small portfolio size, discipline gates on every call, monthly call postmortems, logs executed trades to trading-journal. Modes: daily, weekly, deep, chain, trade, doctor."
metadata:
  hermes:
    category: productivity
---

# invest-recon

**Trigger**: `/invest-recon [daily|weekly|deep <name>|chain <name or theme>|trade ...|doctor]` or "/invest", "run invest recon", "market pulse", "portfolio review", or the operator asking about a specific stock/company ("should I look at X", "is X overvalued") → `deep`, or about suppliers/components/who-benefits ("what components does X use", "picks and shovels for X") → `chain`
**Domain**: productivity (finance)
**Automation**: remote via Hermes cron — daily pulse 07:30 Australia/Sydney Mon–Fri (just after US close), weekly review Saturday 09:00. Delivers TL;DR to Telegram when a channel exists.

## Description

Investing recon for an Australia-based operator trading globally through moomoo AU.
The operator executes all trades manually; this skill only produces information and
ranked recommendations. Companion skill: `trading-journal` (P&L log lives there).

Design intent, in priority order: **passive** (minimal trades, minimal screen time),
**fee-aware** (small portfolio — costs dominate), **grounded** (credible sources only),
**decision-quality over frequency** (the default weekly outcome is "no action"),
**educational** (the operator wants to learn, not point-and-click — see Plain-English
rule below).

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
- **Gamble sleeve** (barbell): every position and call carries a label —
  **Conviction** (thesis rests on current fundamentals) or **Gamble** (thesis
  rests on a low-probability/high-payoff future already expensively priced —
  e.g. a fresh mega-IPO at ~100× sales). Gamble positions live inside the
  satellite but are additionally capped at **10% of total portfolio value
  combined**, and a single gamble at 5%. Gambles pass every gate like any other
  call — the label changes the cap, never the discipline. The operator may take
  gambles; the sleeve exists so a wipeout stings but never wounds. Say the label
  out loud in every call: "this is a Gamble, sized as one."

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

## Plain-English rule — every output, no exceptions

The operator is an intellectual learning the domain, not a client to be handled.
Every piece of financial jargon that appears in a digest gets translated inline,
once, in one clause — e.g. "trading at ~100× sales (you pay $100 today for every
$1 of yearly revenue — the price assumes decades of near-perfect growth)", or
"lockup expiry (the date insiders are first allowed to sell; extra supply often
pressures the price)". Never dumb down the *reasoning* — show the actual
valuation math, the actual mechanism — only translate the *vocabulary*. A
verdict without a visible why is a failure; the goal is that after six months of
digests the operator can make these judgement calls unaided.

## Cross-skill intel bridge

The bugle skills already write sourced digests into the vault. Read them as an
extra signal layer — local files, no new fetches, and they satisfy the
credible-source rule because they cite outlets themselves:

- Global: `<vault>/Agentic Output/digests/<date>*.md`
- Regional: `<vault>/Agentic Output/digests/regional/<region>/<date>*.md`
- AI/tech: `<vault>/Agentic Output/insights/<date>*.md`

Daily: read today's (and, if missing, yesterday's). Weekly: read the past 7
days'. Flag only items touching holdings, watchlist, macro (rates, AUD), or a
plausible new theme — cite the underlying outlet the digest cites, not the
digest. Missing digest files are not an error; note them in Source health and
move on. These digests are signal for *what is happening*; valuation and
tradability work stays with this skill.

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
price_at_call, invalidation, gate_result, label conviction/gamble, taken
true/false, outcome — outcome stays null until scored by a postmortem; the
label lets postmortems report gamble vs conviction hit rates separately, which
is the honest way to learn whether the gambles are earning their sleeve),
`seen` story-dedupe list (21-day
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
5. **Intel bridge**: per the Cross-skill intel bridge section — anything in
   today's bugle/insights digests touching holdings, watchlist, or macro. One
   line per item or "nothing relevant". Signal only, never a trade call.
6. **TL;DR**: 3–5 bullets, the market day in one line each, only stories relevant
   to holdings, watchlist, or macro (rates, AUD).
7. **Source health**: failed fetches or missing bugle digests, or "all green".

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
4. **Discovery** — the idea-generation step; without it the review structurally
   converges to "no action" forever. Scan two inputs: (a) the week's credible
   press for earnings movers, thematic momentum, and unusual sourced stories;
   (b) the past 7 days of bugle/insights digests per the Cross-skill intel
   bridge. Surface **2–3 candidates max**, each with one-paragraph thesis, why
   now, Conviction/Gamble label, and what would make it a Buy. The best go to
   the watchlist with a concrete trigger; the rest are named and dropped.
   "Nothing credible surfaced this week" is a valid and honest outcome. A
   candidate is never a Buy in the same week it's discovered — it enters Watch
   first unless an earnings-driven repricing makes waiting demonstrably costly
   (justify in one line).
5. **Fee check**: round-trip cost math for any Buy/Sell call.
6. **Watchlist hygiene**: drop entries whose thesis expired; say why.
7. **Gaps** (one line, optional): what the source pool missed this week, if anything.
8. **Learnings**: append notable ones to
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

### `/invest-recon deep <ticker or company>` — on-demand single-stock dossier

The "curious about a stock at 10pm" mode. Interactive only, never cron. Produces
a dossier (chat + optionally `<vault>/Agentic Output/invest/deep-<slug>-<date>.md`
if substantial), sections in order:

1. **What the business actually is** — how it makes money, in plain English.
   One paragraph, no investor-deck language.
2. **Tradability from moomoo AU** — listed where, buyable or not. If not
   directly buyable (foreign exchange, private), name the closest tradable
   proxy and honestly state how diluted the exposure is. Never present a proxy
   as equivalent.
3. **Valuation in plain English** — the relevant multiple(s) with the
   translation clause (Plain-English rule), compared against 2–3 named peers,
   ending with "what the price assumes": the growth story you're paying for at
   this price, and what happens if reality is merely good instead of perfect.
4. **Trend & drivers** — what's moved the stock recently and the sourced
   argument for/against continuation. Price data from a data source, never
   from prose.
5. **Bear case** — strongest sourced argument against (standing requirement).
6. **Risk-event calendar** — knowable dated risks: next earnings, lockup
   expiry for recent IPOs, major product/regulatory decisions. Explain the
   mechanism of each once.
7. **Verdict** — **Conviction candidate / Gamble candidate / Pass**, with
   visible reasoning. If candidate: draft thesis + invalidation + horizon and
   run the full pre-trade gate (sizing under the gamble-sleeve cap when
   labeled Gamble). GO → recommend adding to watchlist (the buy decision still
   belongs to a weekly review unless the daily urgent gate would fire). Pass →
   say plainly why, so the operator learns the filter, not just the answer.

Log a `watch` entry in `calls[]` for any candidate verdict. `deep` never
executes anything and is exempt from the trade budget (it's research, not a
trade), but any resulting buy is not.

### `/invest-recon chain <company or theme>` — supply-chain / picks-and-shovels map

For "who actually gets paid when X booms?" Interactive only. Steps:

1. **Map the value chain** — the spend the boom must flow through: components,
   equipment, materials, infrastructure, services. Name real companies per
   link, from credible sources (filings and quality press, not listicles).
2. **Score revenue exposure** — the make-or-break filter: for each candidate,
   estimate what share of *its* revenue comes from this theme (from filings/
   press). A supplier at 3% exposure is not a play on the theme; say so and
   cut it. Prefer companies where the theme is a large or fast-growing share.
3. **Check capture** — does the target company vertically integrate (build
   in-house) or squeeze its suppliers? A famously integrated buyer (e.g.
   SpaceX building ~85% in-house) makes its supplier trade structurally thin —
   state this upfront rather than forcing weak candidates.
4. **Filter to tradable** — keep only what moomoo AU can trade (US-listed
   default); for a strong link that isn't tradable, name it anyway and give
   the nearest tradable alternative with the dilution caveat.
5. **Output** — ranked shortlist of ≤5: one-line role in the chain, revenue
   exposure %, valuation one-liner (plain English), Conviction/Gamble label.
   Top 1–2 get the full `deep` treatment inline if the operator asks, or a
   watchlist entry with trigger. "This chain has no good pure-play" is a
   valid, honest result.

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

Fetch one item from each source tier, report reachable/broken, and verify:
- `portfolio.json` parses, and every `calls[]` entry has the required fields
  (date, type, ticker, price_at_call, invalidation, gate_result, taken).
- Vault path resolves.
- Intel-bridge paths exist and contain recent files (a digest from the last
  3 days under `Agentic Output/digests/` and `Agentic Output/insights/`) —
  stale or missing means the upstream bugle cron is likely broken; flag it,
  don't fail.

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
