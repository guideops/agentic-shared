#!/usr/bin/env python3
"""Direct Google Sheets writer using a service-account key.

No n8n, no OAuth redirect, no webhook. The service account signs a JWT, trades
it for an access token, and talks to the Sheets REST API.

Rows are matched on `listing_id` and updated in place; unseen ids are appended.
That keeps every row at a stable position, so notes you add in columns beyond
the bot's block stay lined up with the listing they belong to.
"""
from __future__ import annotations

import json
import pathlib
import time
import urllib.parse
import urllib.request

import jwt  # PyJWT

TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
API = "https://sheets.googleapis.com/v4/spreadsheets"


class SheetError(RuntimeError):
    pass


def _post(url, data, headers=None, form=False):
    body = urllib.parse.urlencode(data).encode() if form else json.dumps(data).encode()
    h = {"Content-Type": "application/x-www-form-urlencoded" if form
         else "application/json"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=body, headers=h, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b"null")


def _get(url, headers):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b"null")


def access_token(key_path: pathlib.Path) -> str:
    info = json.loads(key_path.read_text())
    for field in ("client_email", "private_key"):
        if not info.get(field):
            raise SheetError(f"service account key is missing '{field}'")
    now = int(time.time())
    assertion = jwt.encode(
        {"iss": info["client_email"], "scope": SCOPE, "aud": TOKEN_URL,
         "iat": now, "exp": now + 3600},
        info["private_key"], algorithm="RS256")
    res = _post(TOKEN_URL, {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion}, form=True)
    if "access_token" not in res:
        raise SheetError(f"token exchange failed: {res}")
    return res["access_token"]


def _col(n: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA."""
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def sync(spreadsheet_id: str, key_path: pathlib.Path, columns: list[str],
         rows: list[dict], sheet_gid: int = 0) -> int:
    """Write rows, matching on listing_id. Returns how many cells' rows changed."""
    tok = access_token(key_path)
    H = {"Authorization": f"Bearer {tok}"}

    meta = _get(f"{API}/{spreadsheet_id}?fields=sheets(properties(sheetId,title))", H)
    title = next((s["properties"]["title"] for s in meta.get("sheets", [])
                  if s["properties"]["sheetId"] == sheet_gid), None)
    if title is None:
        raise SheetError(f"no sheet with gid {sheet_gid} in that spreadsheet")

    last = _col(len(columns) - 1)
    q = urllib.parse.quote(f"{title}!A1:{last}")
    existing = _get(f"{API}/{spreadsheet_id}/values/{q}", H).get("values", [])

    # Refuse to write into a tab that already belongs to something else.
    # Writing the header over row 1 of a populated, unrelated tab destroys data
    # that cannot be recovered through this API - it has happened once already.
    header = existing[0] if existing else []
    updates = []
    if not header:
        if len(existing) > 1:
            raise SheetError(
                f"'{title}' has {len(existing)} rows of data but no header - "
                "refusing to write in case it belongs to something else")
        updates.append({"range": f"{title}!A1:{last}1", "values": [columns]})
        existing = []
    elif header[:len(columns)] == columns:
        existing = existing[1:]
    else:
        raise SheetError(
            f"'{title}' row 1 is {header[:4]}... which is not this table's "
            f"header ({columns[:4]}...). Refusing to overwrite it.")

    id_col = columns.index("listing_id")
    where = {}
    for i, r in enumerate(existing):
        if len(r) > id_col and r[id_col]:
            where[str(r[id_col])] = i + 2          # 1-based, +1 for the header

    def cells(row):
        return [("" if row.get(c) is None else str(row.get(c))) for c in columns]

    appends = []
    for row in rows:
        lid = str(row.get("listing_id", ""))
        if lid in where:
            n = where[lid]
            updates.append({"range": f"{title}!A{n}:{last}{n}", "values": [cells(row)]})
        else:
            appends.append(cells(row))

    if updates:
        _post(f"{API}/{spreadsheet_id}/values:batchUpdate",
              {"valueInputOption": "USER_ENTERED", "data": updates}, headers=H)
    if appends:
        rng = urllib.parse.quote(f"{title}!A1")
        _post(f"{API}/{spreadsheet_id}/values/{rng}:append"
              f"?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS",
              {"values": appends}, headers=H)
    return len(updates) + len(appends)


def read_links(spreadsheet_id: str, key_path: pathlib.Path, gids: list[int]) -> list[str]:
    """Every http(s) value on the given tabs. Strictly read-only - these are the
    operator's own hand-curated tabs and nothing here may write to them."""
    tok = access_token(key_path)
    H = {"Authorization": f"Bearer {tok}"}
    meta = _get(f"{API}/{spreadsheet_id}?fields=sheets(properties(sheetId,title))", H)
    titles = {s["properties"]["sheetId"]: s["properties"]["title"]
              for s in meta.get("sheets", [])}
    out = []
    for gid in gids:
        title = titles.get(gid)
        if not title:
            continue
        q = urllib.parse.quote(f"{title}!A1:Z1000")
        for row in _get(f"{API}/{spreadsheet_id}/values/{q}", H).get("values", []):
            for cell in row:
                c = str(cell).strip()
                if c.startswith("http://") or c.startswith("https://"):
                    out.append(c)
    return out


def replace(spreadsheet_id: str, key_path: pathlib.Path, columns: list[str],
            rows: list[dict], sheet_gid: int = 0,
            signature: set | None = None) -> int:
    """Rewrite a bot-OWNED tab so it exactly mirrors the table.

    Only for a tab nothing else writes to. It clears the block first, so a row
    that no longer meets the criteria disappears instead of lingering - which
    `sync` cannot do, since appending never removes. The same header guard
    applies: a tab whose row 1 belongs to someone else is refused.
    """
    tok = access_token(key_path)
    H = {"Authorization": f"Bearer {tok}"}
    meta = _get(f"{API}/{spreadsheet_id}?fields=sheets(properties(sheetId,title))", H)
    title = next((s["properties"]["title"] for s in meta.get("sheets", [])
                  if s["properties"]["sheetId"] == sheet_gid), None)
    if title is None:
        raise SheetError(f"no sheet with gid {sheet_gid} in that spreadsheet")

    last = _col(len(columns) - 1)
    q = urllib.parse.quote(f"{title}!1:1")
    header = (_get(f"{API}/{spreadsheet_id}/values/{q}", H).get("values") or [[]])[0]
    # An owned tab may legitimately change shape between versions, so identify
    # OUR header by its signature columns rather than demanding an exact match -
    # otherwise adding a column locks the bot out of its own tab. A tab without
    # that signature belongs to someone else and is still refused outright.
    sig = signature if signature is not None else {"listing_id", "shortlist_rank"}
    ours = sig <= set(header)
    if header and not ours:
        raise SheetError(
            f"'{title}' row 1 is {header[:4]}... which is not this table's header. "
            "Refusing to overwrite it.")

    wipe = urllib.parse.quote(f"{title}!A1:{last}")
    _post(f"{API}/{spreadsheet_id}/values/{wipe}:clear", {}, headers=H)

    values = [columns] + [
        [("" if r.get(c) is None else str(r.get(c))) for c in columns] for r in rows]
    body = {"valueInputOption": "USER_ENTERED",
            "data": [{"range": f"{title}!A1:{last}{len(values)}", "values": values}]}
    _post(f"{API}/{spreadsheet_id}/values:batchUpdate", body, headers=H)
    return len(rows)


def read_table(spreadsheet_id: str, key_path: pathlib.Path, gid: int) -> list[dict]:
    """Read a tab as dicts keyed by its row-1 headers. Read-only."""
    tok = access_token(key_path)
    H = {"Authorization": f"Bearer {tok}"}
    meta = _get(f"{API}/{spreadsheet_id}?fields=sheets(properties(sheetId,title))", H)
    title = next((s["properties"]["title"] for s in meta.get("sheets", [])
                  if s["properties"]["sheetId"] == gid), None)
    if title is None:
        raise SheetError(f"no sheet with gid {gid}")
    q = urllib.parse.quote(f"{title}!A1:Z1000")
    vals = _get(f"{API}/{spreadsheet_id}/values/{q}", H).get("values", [])
    if not vals:
        return []
    hdr = [h.strip() for h in vals[0]]
    out = []
    for r in vals[1:]:
        r = list(r) + [""] * (len(hdr) - len(r))
        row = {hdr[i]: r[i] for i in range(len(hdr)) if hdr[i]}
        if any(str(v).strip() for v in row.values()):
            out.append(row)
    return out


def ensure_tab(spreadsheet_id: str, key_path: pathlib.Path, title: str) -> int:
    """Return the gid of `title`, creating the tab if it does not exist."""
    tok = access_token(key_path)
    H = {"Authorization": f"Bearer {tok}"}
    meta = _get(f"{API}/{spreadsheet_id}?fields=sheets(properties(sheetId,title))", H)
    for s in meta.get("sheets", []):
        if s["properties"]["title"] == title:
            return s["properties"]["sheetId"]
    res = _post(f"{API}/{spreadsheet_id}:batchUpdate",
                {"requests": [{"addSheet": {"properties": {"title": title}}}]},
                headers=H)
    return res["replies"][0]["addSheet"]["properties"]["sheetId"]


def set_yes_no(spreadsheet_id: str, key_path: pathlib.Path, gid: int,
               col_index: int, n_rows: int,
               options=("Yes", "No", "Off market", "Off market - Yes")):
    """Put a Yes/No dropdown on one column, for rows 2..n+1.

    The tab is rewritten every run, so the validation has to be re-applied each
    time; the VALUES are carried over separately from state, not from here.
    """
    tok = access_token(key_path)
    H = {"Authorization": f"Bearer {tok}"}
    rng = {"sheetId": gid, "startRowIndex": 1,
           "endRowIndex": max(n_rows + 1, 2),
           "startColumnIndex": col_index, "endColumnIndex": col_index + 1}
    req = {"requests": [{"setDataValidation": {
        "range": rng,
        "rule": {"condition": {"type": "ONE_OF_LIST",
                               "values": [{"userEnteredValue": o} for o in options]},
                 "showCustomUi": True, "strict": False}}}]}
    _post(f"{API}/{spreadsheet_id}:batchUpdate", req, headers=H)


def write_block(spreadsheet_id: str, key_path: pathlib.Path, gid: int,
                first_col: int, header: list[str], rows: list[list]) -> int:
    """Write a rectangular block starting at `first_col`, touching nothing else.

    For annotating a tab this code does not own: the operator's own columns are
    never read back, cleared, or rewritten - only the columns to their right.
    """
    tok = access_token(key_path)
    H = {"Authorization": f"Bearer {tok}"}
    meta = _get(f"{API}/{spreadsheet_id}?fields=sheets(properties(sheetId,title))", H)
    title = next((s["properties"]["title"] for s in meta.get("sheets", [])
                  if s["properties"]["sheetId"] == gid), None)
    if title is None:
        raise SheetError(f"no sheet with gid {gid}")
    a, b = _col(first_col), _col(first_col + len(header) - 1)
    values = [header] + [[("" if v is None else str(v)) for v in r] for r in rows]
    rng = urllib.parse.quote(f"{title}!{a}1:{b}{len(values)}")
    _post(f"{API}/{spreadsheet_id}/values:batchUpdate",
          {"valueInputOption": "USER_ENTERED",
           "data": [{"range": f"{title}!{a}1:{b}{len(values)}", "values": values}]},
          headers=H)
    return len(rows)


def set_row_highlight(spreadsheet_id: str, key_path: pathlib.Path, gid: int,
                      n_rows: int, n_cols: int):
    """Shade a row light red when its verdict is No or an off-market state.

    Deliberately pale: the point is to let the eye skip those rows, not to make
    the text hard to read. Existing rules on the tab are cleared first, or a
    daily re-run would stack a duplicate rule every morning.
    """
    tok = access_token(key_path)
    H = {"Authorization": f"Bearer {tok}"}
    meta = _get(f"{API}/{spreadsheet_id}"
                f"?fields=sheets(properties(sheetId),conditionalFormats)", H)
    existing = 0
    for sh in meta.get("sheets", []):
        if sh.get("properties", {}).get("sheetId") == gid:
            existing = len(sh.get("conditionalFormats") or [])

    reqs = [{"deleteConditionalFormatRule": {"sheetId": gid, "index": i}}
            for i in range(existing - 1, -1, -1)]
    reqs.append({"addConditionalFormatRule": {"index": 0, "rule": {
        "ranges": [{"sheetId": gid, "startRowIndex": 1,
                    "endRowIndex": max(n_rows + 1, 2),
                    "startColumnIndex": 0, "endColumnIndex": n_cols}],
        "booleanRule": {
            "condition": {"type": "CUSTOM_FORMULA", "values": [
                {"userEnteredValue":
                 '=OR($A2="No", LEFT($A2,10)="Off market")'}]},
            "format": {"backgroundColor": {"red": 0.988, "green": 0.886,
                                           "blue": 0.886}}}}}})
    _post(f"{API}/{spreadsheet_id}:batchUpdate", {"requests": reqs}, headers=H)
    return existing
