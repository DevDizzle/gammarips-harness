#!/usr/bin/env python3
"""behavior_log.py — validator/appender for eval/behavior-ledger.jsonl (the /coach substrate).

One row per behavioral EVENT — a leak, a win, or an observation — always anchored to
broker-verifiable evidence. The ledger exists so coaching runs on receipts, not vibes:
"you've done this 3 times, it cost $490" beats any lecture. Wins are recorded with the
same rigor as leaks; the encouragement half of /coach is receipts too.

Usage:
  python scripts/behavior_log.py upsert '<row-json or [rows]>'
  python scripts/behavior_log.py check
  python scripts/behavior_log.py summary [--days N]

Row schema:
  date         YYYY-MM-DD (the event date)
  type         leak | win | observation
  pattern      kebab-case pattern slug (see PATTERNS; new slugs allowed but printed
               for review so vocabulary drift stays visible)
  ticker       ticker or null
  impact_usd   signed number or null (unquantifiable events carry null, never a guess)
  impact_kind  realized | forgone | avoided | none
  evidence     REQUIRED — the broker-sourced or transcript-sourced fact, one line
  source       broker | transcript | memory | funnel
  note         optional color
Key: (date, ticker, pattern) — upsert replaces on collision.
"""
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "eval" / "behavior-ledger.jsonl"

TYPES = {"leak", "win", "observation"}
IMPACT_KINDS = {"realized", "forgone", "avoided", "none"}
# Established vocabulary. Not a closed set — a new slug is accepted but announced,
# so the vocabulary grows deliberately instead of fragmenting silently.
PATTERNS = {
    "revenge-add", "fat-finger", "off-consult-entry", "oversize", "second-position",
    "earnings-unchecked", "rode-past-stop", "rode-to-zero", "exit-at-ask",
    "unrested-target", "recollection-drift", "pre-named-exit", "fast-loser-cut",
    "rotation", "plan-adherence", "impulse-averted", "hold-and-hope",
    "early-exit-regret", "rules-split",
}


def fail(msg):
    print(f"BEHAVIOR-LOG ERROR: {msg}")
    sys.exit(1)


def validate(row, where=""):
    for key in ("date", "type", "pattern", "evidence", "source", "impact_kind"):
        if key not in row or row[key] in (None, ""):
            fail(f"{where}missing key '{key}'")
    if row["type"] not in TYPES:
        fail(f"{where}bad type '{row['type']}'")
    if row["impact_kind"] not in IMPACT_KINDS:
        fail(f"{where}bad impact_kind '{row['impact_kind']}'")
    if (row.get("impact_usd") is None) != (row["impact_kind"] == "none"):
        fail(f"{where}impact_usd null iff impact_kind 'none' "
             f"(got {row.get('impact_usd')}/{row['impact_kind']})")
    try:
        date.fromisoformat(row["date"])
    except ValueError:
        fail(f"{where}date not YYYY-MM-DD")
    if row["pattern"] not in PATTERNS:
        print(f"BEHAVIOR-LOG NOTE: new pattern slug '{row['pattern']}' — "
              f"deliberate vocabulary growth, or a near-duplicate of an existing slug?")


def load():
    if not LOG.exists():
        return []
    rows = []
    for i, line in enumerate(LOG.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            fail(f"line {i}: not valid JSON ({e})")
    return rows


def key(r):
    return (r["date"], r.get("ticker") or "", r["pattern"])


def save(rows):
    rows.sort(key=lambda r: (r["date"], r.get("ticker") or "", r["pattern"]))
    LOG.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows))


def cmd_upsert(payload):
    incoming = json.loads(payload)
    if isinstance(incoming, dict):
        incoming = [incoming]
    for i, row in enumerate(incoming):
        validate(row, where=f"row {i}: ")
    existing = {key(r): r for r in load()}
    new = replaced = 0
    for row in incoming:
        if key(row) in existing:
            replaced += 1
        else:
            new += 1
        existing[key(row)] = row
    save(list(existing.values()))
    print(f"BEHAVIOR-LOG: upserted {new} new, {replaced} replaced ({len(existing)} total rows)")


def cmd_check():
    rows = load()
    for i, r in enumerate(rows):
        validate(r, where=f"line {i+1}: ")
    print(f"BEHAVIOR-LOG: clean ({len(rows)} rows, "
          f"{len({r['date'] for r in rows})} days)")


def cmd_summary(days=None):
    rows = load()
    if days:
        cutoff = (date.today() - timedelta(days=days)).isoformat()
        rows = [r for r in rows if r["date"] >= cutoff]
    by_pattern = defaultdict(lambda: {"n": 0, "usd": 0.0, "quantified": 0})
    for r in rows:
        b = by_pattern[(r["type"], r["pattern"])]
        b["n"] += 1
        if r.get("impact_usd") is not None:
            b["usd"] += r["impact_usd"]
            b["quantified"] += 1
    print(f"{'type':12}{'pattern':22}{'n':>3}{'quantified':>11}{'impact $':>10}")
    for (t, p), b in sorted(by_pattern.items(), key=lambda kv: (kv[0][0], kv[1]["usd"])):
        print(f"{t:12}{p:22}{b['n']:>3}{b['quantified']:>11}{b['usd']:>10.0f}")
    leaks = sum(b["usd"] for (t, _), b in by_pattern.items() if t == "leak")
    wins = sum(b["usd"] for (t, _), b in by_pattern.items() if t == "win")
    print(f"\nleak impact total: {leaks:+.0f}   win impact total: {wins:+.0f}"
          f"   (impact_kind mixed - realized/forgone/avoided; read rows before citing)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in {"upsert", "check", "summary"}:
        fail("usage: upsert '<json>' | check | summary [--days N]")
    if args[0] == "upsert":
        if len(args) < 2:
            fail("upsert needs a JSON payload")
        cmd_upsert(args[1])
    elif args[0] == "check":
        cmd_check()
    else:
        days = None
        if "--days" in args:
            days = int(args[args.index("--days") + 1])
        cmd_summary(days)
