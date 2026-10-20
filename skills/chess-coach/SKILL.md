---
name: chess-coach
description: "Chess improvement coach for the operator's 300→1500 chess.com goal. The nightly Hermes cron job (chess-coach-nightly, no-agent mode, 17:30 UTC) runs scripts/nightly.py headlessly via ~/.hermes/scripts/chess-coach-run.sh — pure Python + Stockfish, no LLM — pulling games from the chess.com API, flagging blunders, and writing the morning note, drills, and dashboard into the vault. Use this skill interactively when the user says /chess-coach, 'chess coach', 'analyse my chess', 'chess review'. Args: 'setup <username>', 'today', 'weekly', 'status', 'insight'. Never asks questions in headless runs."
metadata:
  short-description: Nightly Stockfish analysis of your chess.com games → Obsidian morning note + drills
---

# Chess Coach

Purpose: drive blunders-per-game down; rating follows. Gates: 600 → 900 → 1200 → 1500 (rapid).

## Layout

- `config.json` — username, vault target, thresholds. `username: SET_ME` means not yet configured.
- `scripts/nightly.py` — the whole pipeline. Run with `venv/bin/python` (needs python-chess). Idempotent; `--date YYYY-MM-DD` and `--weekly` flags for testing/backfill.
- `data/state.json` — last processed game, blunder bank (spaced repetition: 1/3/7/16/35 days), served puzzles, rating history.
- `data/puzzles.csv` — 4,000 lichess puzzles (CC0), ratings 400–1399, 400 per band.
- `data/openings.tsv` — lichess opening names (CC0) for labelling games.
- Vault output: `<vault>/Agentic Output/chess/coach/` — daily `YYYY-MM-DD.md`, `Dashboard.md`, `weekly/`.
- Scheduling: Hermes cron job `chess-coach-nightly` (`hermes cron list`), `--no-agent`, runs `~/.hermes/scripts/chess-coach-run.sh` daily 17:30 UTC. Not a systemd timer — this project briefly used one (2026-08-05) before being migrated to match the other coach skills so it's visible in the AW kanban.
- The reading library is separate: `<vault>/Agentic Output/chess/library/` (see its `00 Start Here.md`).

## Invocation modes

- `/chess-coach setup <username>` → write the username into `config.json`, then run `today` to verify the account resolves and produce the first note.
- `/chess-coach today` → run `venv/bin/python scripts/nightly.py` now, then summarize the morning note conversationally.
- `/chess-coach weekly` → run `nightly.py --weekly`, then read this week's note in `coach/weekly/` **and the daily notes it covers**, and append a `## Coach insight` section to that weekly note with the judgement layer (same rules as `insight` below). The `## Coach insight` heading is load-bearing: the Sunday cron job (`chess-coach-weekly-run.sh`) greps for it as its idempotency guard, so never rename it or skip writing it.
- `/chess-coach status` → read `Dashboard.md` + state.json; report trend, next gate, drill backlog. No analysis run.
- `/chess-coach insight` → read the last 7 daily notes and the blunder bank; identify the recurring pattern the heuristics can't see (e.g. "all three knight losses came from advancing pawns loosening your own defenders"); write a short addendum section `## Coach insight` appended to today's note. This is the only mode where the LLM adds analysis — keep it to one pattern and one instruction, not a lecture.

## Rules

- Headless (cron/systemd) runs are Python-only and never invoke an LLM; if something fails the service logs to journald — fail loudly, never improvise output.
- Never lower `blunder_cp` below 200 or raise drills above 5/day — volume kills the habit (same lesson as the language coaches: small daily beats big sporadic).
- When the operator's rapid rating passes 1200: regenerate `data/puzzles.csv` from the lichess dump with bands up to 2000 (the current slice caps at 1399), and update the Openings Guide gates in the library.
- 2-week keep-or-kill trial from first real run: if the operator isn't reading the morning notes by then, reshape or kill (record the verdict in memory).
- Interactive `insight`/`weekly` follow the operator's real-talk preference: name the uncomfortable pattern plainly; no cheerleading.
