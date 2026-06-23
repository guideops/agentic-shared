---
name: trading-journal
description: "Log trades, calculate P&L, identify patterns, and generate daily/weekly trading performance reports. Saves to `domains/productivity/trading/`."
metadata:
  hermes:
    category: productivity
---

# trading-journal

**Trigger**: `/trading-journal` or "log trade", "journal trade", "trading update"
**Domain**: productivity
**Automation**: local (on-demand) + remote (daily P&L summary)

## Description
Log trades, calculate P&L, identify patterns, and generate daily/weekly trading performance reports. Saves to `domains/productivity/trading/`.

## Instructions
1. Accept trade entry (inline or interactive):
   - Asset, direction (long/short), entry price, exit price, size, date/time, setup type, outcome.
2. Calculate: P&L (absolute + %), R:R ratio, win/loss.
3. Append to `domains/productivity/trading/journal.md`.
4. After logging, analyze last 20 trades:
   - Win rate, avg win vs avg loss, expectancy
   - Best/worst setup types
   - Streak (current W/L run)
5. Flag patterns: "3 consecutive losses on FOMO entries — review setup discipline."
6. Weekly: generate performance report → save to `domains/productivity/trading/reports/YYYY-WW.md`.

## Input
Inline: `/trading-journal long BTC 60000 62000 0.1 BTC breakout`
Or interactive fields.

## Output
Appended to `domains/productivity/trading/journal.md`:
```markdown
## 2026-05-08 14:30
- Asset: BTC/USD
- Direction: Long
- Entry: $60,000 | Exit: $62,000
- Size: 0.1 BTC
- P&L: +$200 (+3.33%)
- R:R: 1:2
- Setup: Breakout
- Notes: ...
```

## Automation
Remote (daily): GitHub Actions 21:00 UTC → generate daily P&L summary → push to `wiki/productivity/trading/` → optional Substack/email.
