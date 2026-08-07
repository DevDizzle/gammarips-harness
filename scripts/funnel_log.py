#!/usr/bin/env python3
"""funnel_log.py — validator/appender for eval/funnel-log.jsonl (see eval/README.md).

Usage:
  python scripts/funnel_log.py upsert '<row-json or [rows]>'
  python scripts/funnel_log.py check
  python scripts/funnel_log.py summary [--days N]
"""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "eval" / "funnel-log.jsonl"

STAGES = {"pool", "shortlist", "candidate", "entered"}
REASONS = {
    "delta_band", "moneyness_below", "moneyness_above", "live_drift", "liquidity",
    "earnings", "head_to_head", "operator_declined", "timing", "regime",
    "sizing",   # RETIRED 2026-08-05 — kept so historical rows validate. Never emit a new one:
                # the screen no longer drops on contract price (docs/RULES.md §Sizing).
    "none",
}
SCAN_KEYS = {"delta", "moneyness_pct", "overnight_score", "mom_60", "mid"}


def fail(msg):
    print(f"FUNNEL-LOG ERROR: {msg}")
    sys.exit(1)


def validate(row, where=""):
    for key in ("entry_day", "scan_date", "ticker", "contract", "funnel_stage",
                "exclusion_reason", "scan"):
        if key not in row:
            fail(f"{where}missing key '{key}'")
    if row["funnel_stage"] not in STAGES:
        fail(f"{where}bad funnel_stage '{row['funnel_stage']}'")
    if row["exclusion_reason"] not in REASONS:
        fail(f"{where}bad exclusion_reason '{row['exclusion_reason']}'")
    if (row["exclusion_reason"] == "none") != (row["funnel_stage"] == "entered"):
        fail(f"{where}exclusion_reason 'none' iff funnel_stage 'entered' "
             f"(got {row['funnel_stage']}/{row['exclusion_reason']})")
    if not isinstance(row["scan"], dict) or not SCAN_KEYS <= set(row["scan"]):
        fail(f"{where}scan must contain {sorted(SCAN_KEYS)}")
    for block in ("outcome_session", "outcome_3d"):
        if row.get(block) is not None and not isinstance(row[block], dict):
            fail(f"{where}{block} must be object or null")
    for dkey in ("entry_day", "scan_date"):
        try:
            date.fromisoformat(row[dkey])
        except ValueError:
            fail(f"{where}{dkey} not YYYY-MM-DD")


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


def save(rows):
    LOG.parent.mkdir(exist_ok=True)
    rows.sort(key=lambda r: (r["entry_day"], r["ticker"]))
    LOG.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows))


def cmd_upsert(payload):
    incoming = json.loads(payload)
    if isinstance(incoming, dict):
        incoming = [incoming]
    for i, row in enumerate(incoming):
        validate(row, where=f"upsert[{i}]: ")
    rows = load()
    index = {(r["entry_day"], r["ticker"]): n for n, r in enumerate(rows)}
    added = replaced = 0
    for row in incoming:
        key = (row["entry_day"], row["ticker"])
        if key in index:
            # merge: incoming non-null outcome blocks win; never null-out an existing one
            old = rows[index[key]]
            for block in ("outcome_session", "outcome_3d"):
                if row.get(block) is None and old.get(block) is not None:
                    row[block] = old[block]
            rows[index[key]] = row
            replaced += 1
        else:
            rows.append(row)
            index[key] = len(rows) - 1
            added += 1
    save(rows)
    print(f"FUNNEL-LOG: upserted {added} new, {replaced} replaced "
          f"({len(rows)} total rows)")


def cmd_check():
    rows = load()
    for i, row in enumerate(rows, 1):
        validate(row, where=f"row {i} ({row.get('ticker', '?')}): ")
    days = sorted({r["entry_day"] for r in rows})
    print(f"FUNNEL-LOG: clean ({len(rows)} rows, {len(days)} days"
          f"{', ' + days[0] + '..' + days[-1] if days else ''})")


def pct(x):
    return f"{100 * x:+.1f}%" if x is not None else "—"


def cmd_summary(days_back):
    rows = load()
    if days_back:
        cutoff = (date.today() - timedelta(days=days_back)).isoformat()
        rows = [r for r in rows if r["entry_day"] >= cutoff]
    if not rows:
        print("FUNNEL-LOG: no rows in window")
        return
    groups = {}
    for r in rows:
        key = (r["funnel_stage"], r["exclusion_reason"])
        groups.setdefault(key, []).append(r)
    print(f"{'stage':<10} {'reason':<18} {'n':>4} {'n3d':>4} "
          f"{'t20':>5} {'t40':>5} {'meanMFE':>8} {'meanFin':>8}")
    for (stage, reason), grp in sorted(groups.items()):
        o3 = [g["outcome_3d"] for g in grp
              if g.get("outcome_3d") and g["outcome_3d"].get("status") == "scored"]
        n3 = len(o3)
        t20 = sum(1 for o in o3 if o.get("touched_20")) / n3 if n3 else None
        t40 = sum(1 for o in o3 if o.get("touched_40")) / n3 if n3 else None
        mfes = [o["mfe_pct"] for o in o3 if o.get("mfe_pct") is not None]
        fins = [o["finish_pct"] for o in o3 if o.get("finish_pct") is not None]
        print(f"{stage:<10} {reason:<18} {len(grp):>4} {n3:>4} "
              f"{(f'{100*t20:.0f}%' if t20 is not None else '—'):>5} "
              f"{(f'{100*t40:.0f}%' if t40 is not None else '—'):>5} "
              f"{(pct(sum(mfes)/len(mfes)) if mfes else '—'):>8} "
              f"{(pct(sum(fins)/len(fins)) if fins else '—'):>8}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        fail("usage: upsert '<json>' | check | summary [--days N]")
    if args[0] == "upsert" and len(args) == 2:
        cmd_upsert(args[1])
    elif args[0] == "check":
        cmd_check()
    elif args[0] == "summary":
        days_back = int(args[args.index("--days") + 1]) if "--days" in args else None
        cmd_summary(days_back)
    else:
        fail("usage: upsert '<json>' | check | summary [--days N]")
