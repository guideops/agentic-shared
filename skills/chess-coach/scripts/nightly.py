#!/usr/bin/env python3
"""chess-coach nightly pipeline.

Pulls the operator's chess.com games, finds blunders with Stockfish, writes the
morning note + dashboard into the Obsidian vault, and maintains the blunder bank
(spaced repetition) and puzzle drills. Pure Python — no LLM. Idempotent: safe to
re-run; already-processed games are skipped via state.json.

Usage: nightly.py [--date YYYY-MM-DD] [--weekly]
"""
import argparse, csv, datetime, hashlib, io, json, os, random, re, sys, urllib.request

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL, "venv", "lib"))
import chess, chess.engine, chess.pgn, chess.svg  # noqa: E402  (venv interpreter expected)

CFG = json.load(open(os.path.join(SKILL, "config.json")))
DATA = os.path.join(SKILL, "data")
STATE_PATH = os.path.join(DATA, "state.json")
UA = {"User-Agent": "chess-coach/1.0 (personal training tool; hello@guidantoperations.tech)"}
PIECE_NAMES = {chess.PAWN: "pawn", chess.KNIGHT: "knight", chess.BISHOP: "bishop",
               chess.ROOK: "rook", chess.QUEEN: "queen", chess.KING: "king"}
REVIEW_INTERVALS = [1, 3, 7, 16, 35]  # days


def load_state():
    if os.path.exists(STATE_PATH):
        return json.load(open(STATE_PATH))
    return {"last_end_time": 0, "blunder_bank": [], "served_puzzles": [],
            "ratings": {}, "history": []}


def save_state(state):
    tmp = STATE_PATH + ".tmp"
    json.dump(state, open(tmp, "w"), indent=1)
    os.replace(tmp, STATE_PATH)


def fetch_json(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def fetch_new_games(state, today):
    """Return list of chess.com game dicts newer than state.last_end_time."""
    user = CFG["username"].lower()
    months = [(today.year, today.month)]
    if today.day <= 3:  # catch games from the tail of last month
        prev = (today.replace(day=1) - datetime.timedelta(days=1))
        months.insert(0, (prev.year, prev.month))
    games = []
    for y, m in months:
        try:
            data = fetch_json(f"https://api.chess.com/pub/player/{user}/games/{y}/{m:02d}")
        except Exception as e:
            print(f"WARN: archive {y}-{m:02d} fetch failed: {e}", file=sys.stderr)
            continue
        games.extend(data.get("games", []))
    fresh = [g for g in games if g.get("end_time", 0) > state["last_end_time"]
             and g.get("rules") == "chess" and g.get("pgn")]
    fresh.sort(key=lambda g: g["end_time"])
    return fresh


def load_openings():
    book = []  # (san_tuple, name)
    with open(os.path.join(DATA, "openings.tsv")) as f:
        for row in csv.DictReader(f, delimiter="\t"):
            sans = tuple(t for t in row["pgn"].split() if not t.endswith("."))
            book.append((sans, row["name"]))
    book.sort(key=lambda x: -len(x[0]))
    return book


def name_opening(book, sans):
    sans = tuple(sans)
    for pattern, name in book:
        if sans[:len(pattern)] == pattern:
            return name
    return "Unknown opening"


def cp(score, color):
    """Clamped centipawn value from `color`'s point of view."""
    v = score.pov(color).score(mate_score=2000)
    return max(-1500, min(1500, v))


def game_phase(board):
    if board.fullmove_number <= 10:
        return "opening"
    minor_major = sum(1 for p in board.piece_map().values() if p.piece_type != chess.PAWN) - 2
    return "endgame" if minor_major <= 6 else "middlegame"


def analyse_game(engine, game_dict, user):
    """Return (meta, mistakes[]) for one chess.com game dict."""
    pgn = chess.pgn.read_game(io.StringIO(game_dict["pgn"]))
    if pgn is None:
        return None, []
    white = game_dict["white"]["username"].lower() == user
    color = chess.WHITE if white else chess.BLACK
    me = game_dict["white"] if white else game_dict["black"]
    opp = game_dict["black"] if white else game_dict["white"]
    result = me.get("result", "?")
    won = result == "win"
    drew = result in ("agreed", "repetition", "stalemate", "insufficient", "50move", "timevsinsufficient")
    limit = chess.engine.Limit(time=CFG["analysis_time_per_move"])
    board = pgn.board()
    sans, mistakes = [], []
    info = engine.analyse(board, limit)
    ev_before, best_before = cp(info["score"], color), info.get("pv", [None])[0]
    for move in pgn.mainline_moves():
        san = board.san(move)
        sans.append(san)
        mover_is_me = board.turn == color
        fen_before = board.fen()
        phase = game_phase(board)
        movenum = board.fullmove_number
        board.push(move)
        info = engine.analyse(board, limit)
        ev_after = cp(info["score"], color)
        opp_reply = info.get("pv", [None])[0]
        if mover_is_me and ev_before is not None:
            swing = ev_before - ev_after
            if swing >= CFG["mistake_cp"] and ev_before > CFG["already_lost_cp"] \
                    and best_before is not None and best_before != move:
                kind = "blunder" if swing >= CFG["blunder_cp"] else "mistake"
                b = chess.Board(fen_before)
                best_san = b.san(best_before)
                hint = motif_hint(board, move, opp_reply, best_before, b)
                mistakes.append({
                    "kind": kind, "move_number": movenum, "san": san,
                    "best_san": best_san, "swing": swing, "phase": phase,
                    "fen": fen_before, "hint": hint, "url": game_dict.get("url", ""),
                    "uci": move.uci(), "best_uci": best_before.uci(),
                })
        ev_before, best_before = ev_after, opp_reply
    meta = {
        "url": game_dict.get("url", ""), "time_class": game_dict.get("time_class", "?"),
        "color": "White" if white else "Black", "opponent": opp.get("username", "?"),
        "opp_rating": opp.get("rating"), "my_rating": me.get("rating"),
        "result": "won" if won else ("drew" if drew else "lost"),
        "end_time": game_dict["end_time"], "sans": sans, "n_moves": len(sans),
    }
    return meta, mistakes


def motif_hint(board_after, played, opp_reply, best_move, board_before):
    """One human sentence about what the mistake allowed."""
    if best_move is not None and board_before.gives_check(best_move):
        b2 = board_before.copy(); b2.push(best_move)
        if b2.is_checkmate():
            return "You had a checkmate available."
    if opp_reply is not None and board_after.is_capture(opp_reply):
        victim = board_after.piece_at(opp_reply.to_square)
        if victim and victim.piece_type != chess.PAWN:
            return (f"This left your {PIECE_NAMES[victim.piece_type]} on "
                    f"{chess.square_name(opp_reply.to_square)} to be taken.")
    return "Compare your move with the engine's suggestion in the analysis link."


def lichess_link(fen):
    return "https://lichess.org/analysis/" + fen.replace(" ", "_")


def save_diagram(fen, name, orientation, arrows=()):
    """Render an exact SVG board into coach/diagrams/ (never overwrites). Returns md embed."""
    ddir = os.path.join(CFG["vault_chess_dir"], "coach", "diagrams")
    os.makedirs(ddir, exist_ok=True)
    path = os.path.join(ddir, name)
    if not os.path.exists(path):
        svg = chess.svg.board(chess.Board(fen), orientation=orientation,
                              arrows=list(arrows), size=340)
        open(path, "w").write(svg)
    return f"![](diagrams/{name.replace(' ', '%20')})"


def fen_id(fen):
    return hashlib.md5(fen.encode()).hexdigest()[:8]


def load_motifs():
    return json.load(open(os.path.join(DATA, "motifs.json")))


def update_blunder_bank(state, mistakes, today):
    for m in mistakes:
        if m["kind"] != "blunder":
            continue
        state["blunder_bank"].append({
            "fen": m["fen"], "san": m["san"], "best_san": m["best_san"],
            "swing": m["swing"], "hint": m["hint"], "url": m["url"],
            "added": today.isoformat(), "stage": 0,
            "due": (today + datetime.timedelta(days=REVIEW_INTERVALS[0])).isoformat(),
        })


def due_revenge_drills(state, today):
    due = [b for b in state["blunder_bank"]
           if b["stage"] < len(REVIEW_INTERVALS) and b["due"] <= today.isoformat()]
    due.sort(key=lambda b: b["due"])
    picked = due[:CFG["revenge_drills_per_day"]]
    for b in picked:
        b["stage"] += 1
        if b["stage"] < len(REVIEW_INTERVALS):
            b["due"] = (today + datetime.timedelta(days=REVIEW_INTERVALS[b["stage"]])).isoformat()
    return picked


def pick_fresh_puzzles(state, rating, today, theme=None):
    """Prefer puzzles matching the day's motif theme, fill the rest from any."""
    rating = rating or 500
    lo, hi = rating - 100, rating + 200
    served = set(state["served_puzzles"])
    themed, other = [], []
    with open(os.path.join(DATA, "puzzles.csv")) as f:
        for row in csv.DictReader(f):
            if row["PuzzleId"] not in served and lo <= int(row["Rating"]) <= hi:
                (themed if theme and theme in row["Themes"].split() else other).append(row)
    rng = random.Random(today.toordinal())
    n = CFG["fresh_puzzles_per_day"]
    picked = rng.sample(themed, min(max(n - 1, 1), len(themed)))
    picked += rng.sample(other, min(n - len(picked), len(other)))
    state["served_puzzles"].extend(p["PuzzleId"] for p in picked)
    return picked


def render_puzzle(row, idx):
    board = chess.Board(row["FEN"])
    ucis = row["Moves"].split()
    board.push(chess.Move.from_uci(ucis[0]))  # lichess convention: first move is the setup move
    to_move = "White" if board.turn else "Black"
    fen = board.fen()
    solution = []
    for u in ucis[1:]:
        mv = chess.Move.from_uci(u)
        solution.append(board.san(mv))
        board.push(mv)
    themes = ", ".join(t for t in row["Themes"].split()[:4])
    orientation = chess.WHITE if to_move == "White" else chess.BLACK
    diagram = save_diagram(fen, f"puzzle-{row['PuzzleId']}.svg", orientation)
    return (f"**Puzzle {idx}** ({row['Rating']}) — *{to_move} to move.* Themes: {themes}\n"
            f"{diagram}\n"
            f"Say the full line out loud before you check. "
            f"[Analysis board]({lichess_link(fen)})\n"
            f"> [!question]- Solution\n"
            f"> {' '.join(solution)} · [interactive](https://lichess.org/training/{row['PuzzleId']})\n")


def render_mistake(m, idx, today, game_idx):
    board = chess.Board(m["fen"])
    played = chess.Move.from_uci(m["uci"])
    best = chess.Move.from_uci(m["best_uci"])
    arrows = [chess.svg.Arrow(played.from_square, played.to_square, color="red"),
              chess.svg.Arrow(best.from_square, best.to_square, color="green")]
    diagram = save_diagram(m["fen"], f"{today.isoformat()}-g{game_idx}-mv{m['move_number']}.svg",
                           board.turn, arrows)
    return (f"**{idx}. Move {m['move_number']} — you played `{m['san']}` (red), better was `{m['best_san']}` (green)** "
            f"({m['kind']}, swing {m['swing']/100:.1f} pawns, {m['phase']})\n"
            f"{diagram}\n"
            f"{m['hint']} [Analyse the position]({lichess_link(m['fen'])})\n")


def render_revenge(b, idx):
    board = chess.Board(b["fen"])
    diagram = save_diagram(b["fen"], f"revenge-{fen_id(b['fen'])}.svg", board.turn)
    return (f"**Revenge {idx}** — from your game on {b['added']}. "
            f"You played `{b['san']}` here. Find the better move.\n"
            f"{diagram}\n"
            f"[Analysis board]({lichess_link(b['fen'])})\n"
            f"> [!question]- Solution\n"
            f"> `{b['best_san']}` — {b['hint']} ([original game]({b['url']}))\n")


def write_morning_note(today, results, revenge, puzzles, state, motif):
    coach_dir = os.path.join(CFG["vault_chess_dir"], "coach")
    os.makedirs(coach_dir, exist_ok=True)
    lines = [f"# Chess Coach — {today.isoformat()}", ""]
    if not results:
        lines += ["No new games since the last run. The drills below still count.", ""]
    else:
        n_bl = sum(1 for _, ms in results for m in ms if m["kind"] == "blunder")
        n_g = len(results)
        lines += [f"**{n_g} game{'s' if n_g != 1 else ''} analysed · "
                  f"{n_bl} blunder{'s' if n_bl != 1 else ''} · "
                  f"{n_bl/n_g:.1f} blunders/game** (target: under 1.0)", ""]
        for gi, (meta, ms) in enumerate(results, 1):
            lines.append(f"## {meta['result'].capitalize()} as {meta['color']} vs {meta['opponent']} "
                         f"({meta['opp_rating']}) · {meta['time_class']}")
            lines.append(f"Opening: {meta['opening']} · [game link]({meta['url']})")
            lines.append("")
            if ms:
                for i, m in enumerate(ms, 1):
                    lines.append(render_mistake(m, i, today, gi))
            else:
                lines.append("No mistakes above threshold. Clean game — this is the goal feeling.\n")
    lines.append(f"## Tactic of the day — {motif['name']}")
    lines.append("")
    lines.append(motif["lesson"])
    lines.append("")
    lines.append("## Today's drills (~10 min)")
    lines.append("")
    if revenge:
        for i, b in enumerate(revenge, 1):
            lines.append(render_revenge(b, i))
    for i, p in enumerate(puzzles, 1):
        lines.append(render_puzzle(p, i))
    if not revenge and not puzzles:
        lines.append("No drills available (puzzle pool exhausted at this rating — widen bands in config).")
    lines.append("")
    lines.append("Habit reminder before every move tonight: **checks, captures, threats — theirs first.**")
    path = os.path.join(coach_dir, f"{today.isoformat()}.md")
    open(path, "w").write("\n".join(lines) + "\n")
    print("wrote", path)


def write_dashboard(today, state):
    coach_dir = os.path.join(CFG["vault_chess_dir"], "coach")
    os.makedirs(coach_dir, exist_ok=True)
    hist = state["history"][-200:]
    lines = [f"# Coach Dashboard", "", f"Updated {today.isoformat()}", ""]
    for tc in sorted(state["ratings"]):
        lines.append(f"- **{tc}**: {state['ratings'][tc]}")
    gates = CFG["goal_gates"]
    primary = state["ratings"].get(CFG["primary_time_class"]) or (hist[-1]["rating"] if hist else None)
    if primary:
        nxt = next((g for g in gates if g > primary), None)
        lines.append(f"- **Next gate**: {nxt if nxt else 'GOAL REACHED'} "
                     f"(current {CFG['primary_time_class']}: {primary})")
    lines.append("")
    last20 = hist[-20:]
    if last20:
        bpg = sum(h["blunders"] for h in last20) / len(last20)
        lines.append(f"**Blunders per game (last {len(last20)}): {bpg:.2f}** — this is the number that matters; rating follows it.")
        lines.append("")
        lines.append("| date | class | result | rating | blunders |")
        lines.append("|---|---|---|---|---|")
        for h in reversed(last20):
            lines.append(f"| {h['date']} | {h['time_class']} | {h['result']} | {h['rating']} | {h['blunders']} |")
    bank = state["blunder_bank"]
    active = sum(1 for b in bank if b["stage"] < len(REVIEW_INTERVALS))
    lines += ["", f"Blunder bank: {len(bank)} total, {active} still in rotation."]
    open(os.path.join(coach_dir, "Dashboard.md"), "w").write("\n".join(lines) + "\n")


def write_weekly(today, state):
    coach_dir = os.path.join(CFG["vault_chess_dir"], "coach", "weekly")
    os.makedirs(coach_dir, exist_ok=True)
    iso = today.isocalendar()
    week_ago = (today - datetime.timedelta(days=7)).isoformat()
    wk = [h for h in state["history"] if h["date"] >= week_ago]
    lines = [f"# Week {iso[1]}, {iso[0]} — review", ""]
    if not wk:
        lines.append("No games this week. The plan only works if you play — one rapid game tonight.")
    else:
        bpg = sum(h["blunders"] for h in wk) / len(wk)
        wins = sum(1 for h in wk if h["result"] == "won")
        lines += [f"- Games: {len(wk)} ({wins} wins)",
                  f"- Blunders/game: {bpg:.2f}",
                  f"- Rating now: " + ", ".join(f"{tc} {r}" for tc, r in state["ratings"].items()), ""]
        phases = {}
        for b in state["blunder_bank"]:
            if b["added"] >= week_ago:
                phases[b.get("hint", "")[:40]] = phases.get(b.get("hint", "")[:40], 0) + 1
        if phases:
            top = max(phases.items(), key=lambda kv: kv[1])
            lines.append(f"Most repeated mistake this week: *{top[0]}…* ({top[1]}×). "
                         "That's next week's drill focus — the revenge drills already include these positions.")
    open(os.path.join(coach_dir, f"{iso[0]}-W{iso[1]:02d}.md"), "w").write("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date")
    ap.add_argument("--weekly", action="store_true")
    args = ap.parse_args()
    today = datetime.date.fromisoformat(args.date) if args.date else datetime.date.today()

    if CFG["username"] == "SET_ME":
        note = os.path.join(CFG["vault_chess_dir"], "coach", "SETUP NEEDED.md")
        os.makedirs(os.path.dirname(note), exist_ok=True)
        open(note, "w").write("# Chess coach — setup needed\n\nSet your chess.com username in "
                              "`/opt/agentic/shared/skills/chess-coach/config.json` (`username` field), "
                              "or tell the agent: `/chess-coach setup <username>`.\n")
        print("username not configured; wrote setup note and exiting cleanly")
        return 0

    state = load_state()
    games = fetch_new_games(state, today)
    book = load_openings()
    results = []
    if games:
        engine = chess.engine.SimpleEngine.popen_uci(CFG["stockfish"])
        engine.configure({"Threads": 2, "Hash": 128})
        try:
            for g in games[:12]:  # hard cap per night
                meta, mistakes = analyse_game(engine, g, CFG["username"].lower())
                if meta is None:
                    continue
                meta["opening"] = name_opening(book, meta["sans"])
                results.append((meta, mistakes))
                state["last_end_time"] = max(state["last_end_time"], meta["end_time"])
                state["ratings"][meta["time_class"]] = meta["my_rating"]
                state["history"].append({
                    "date": today.isoformat(), "time_class": meta["time_class"],
                    "result": meta["result"], "rating": meta["my_rating"],
                    "blunders": sum(1 for m in mistakes if m["kind"] == "blunder"),
                })
                update_blunder_bank(state, mistakes, today)
        finally:
            engine.quit()

    revenge = due_revenge_drills(state, today)
    primary = state["ratings"].get(CFG["primary_time_class"])
    fallback = next(iter(state["ratings"].values()), None)
    motifs = load_motifs()
    motif = motifs[today.toordinal() % len(motifs)]
    puzzles = pick_fresh_puzzles(state, primary or fallback, today, theme=motif["theme"])
    write_morning_note(today, results, revenge, puzzles, state, motif)
    write_dashboard(today, state)
    if args.weekly or today.weekday() == 6:
        write_weekly(today, state)
    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
