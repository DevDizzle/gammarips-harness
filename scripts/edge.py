#!/usr/bin/env python3
"""edge.py — does any scan feature separate the day's winners from the rest?

Reads eval/funnel-log.jsonl and answers the only question that improves selection:
of everything the pool offered, what did the winners have that our shortlist didn't?

This is deliberately a script, not a prompt. The answer is a statistic over every
accumulated day, and one day of narrative is noise. It reports its own sample size
first and refuses to dress up an underpowered read as a finding.

    python scripts/edge.py                 # all days, auto basis
    python scripts/edge.py --days 20       # recent window
    python scripts/edge.py --basis session # same-evening replay instead of 3d labels
    python scripts/edge.py --winner mfe --threshold 0.20
"""

import argparse
import json
import math
import pathlib
import sys
from collections import defaultdict

LOG = pathlib.Path(__file__).resolve().parent.parent / "eval" / "funnel-log.jsonl"

# Below these, a separation number is not evidence of anything. Chosen so the banner
# fires on the sample we actually have rather than a hypothetical mature one.
MIN_SCORED = 150
MIN_DAYS = 10
MIN_WINNERS = 20

# The last two are CONTINUATION features, added 2026-08-05 (F-003). Both are in the pool
# and were never carried into the funnel. On an off-funnel study (N=176, 5 entry days) both
# ranked winners LOWER: the names that look hottest at the scan continued least. Recorded
# here so our own data accumulates on them; not yet evidence at our N.
FEATURES = ["delta", "moneyness_pct", "overnight_score", "mom_60", "mid",
            "atr_norm_move", "catalyst_score"]
STAGE_ORDER = ["pool", "shortlist", "candidate", "entered"]


def load(days=None):
    if not LOG.exists():
        sys.exit(f"edge: no funnel log at {LOG}")
    rows = []
    for i, line in enumerate(LOG.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            sys.exit(f"edge: bad JSON on line {i}: {e}")
    if days:
        keep = sorted({r.get("entry_day") for r in rows if r.get("entry_day")})[-days:]
        rows = [r for r in rows if r.get("entry_day") in keep]
    return rows


def outcome(row, basis):
    """Return the scored outcome dict for the requested basis, or None."""
    o3, os_ = row.get("outcome_3d"), row.get("outcome_session")
    if basis == "3d":
        cand = [o3]
    elif basis == "session":
        cand = [os_]
    else:  # auto — prefer the labeled 3d surface, fall back to the evening replay
        cand = [o3, os_]
    for o in cand:
        if isinstance(o, dict) and o.get("status") != "unlabeled":
            if any(o.get(k) is not None for k in ("mfe_pct", "close_pct", "finish_pct")):
                return o
    return None


def is_winner(o, mode, threshold):
    if mode == "touched_20":
        return bool(o.get("touched_20"))
    if mode == "touched_40":
        return bool(o.get("touched_40"))
    mfe = o.get("mfe_pct")
    return mfe is not None and mfe >= threshold


def auc_with_ci(pos, neg):
    """Rank-based separation. 0.50 = the feature tells you nothing.

    Returns (auc, lo, hi) on a 95% Hanley-McNeil interval, or None if degenerate.
    """
    n_p, n_n = len(pos), len(neg)
    if n_p == 0 or n_n == 0:
        return None
    allv = sorted([(v, 1) for v in pos] + [(v, 0) for v in neg], key=lambda t: t[0])
    ranks, i = [0.0] * len(allv), 0
    while i < len(allv):  # average ranks across ties
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    rank_pos = sum(r for r, (_, lab) in zip(ranks, allv) if lab == 1)
    auc = (rank_pos - n_p * (n_p + 1) / 2.0) / (n_p * n_n)
    q1 = auc / (2.0 - auc) if auc < 2 else 0.0
    q2 = 2.0 * auc * auc / (1.0 + auc) if auc > -1 else 0.0
    var = (
        auc * (1 - auc) + (n_p - 1) * (q1 - auc**2) + (n_n - 1) * (q2 - auc**2)
    ) / (n_p * n_n)
    se = math.sqrt(max(var, 0.0))
    return auc, max(0.0, auc - 1.96 * se), min(1.0, auc + 1.96 * se)


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def fmt(v, pct=False):
    if v is None:
        return "  n/a"
    return f"{v*100:6.1f}%" if pct else f"{v:6.3f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, help="restrict to the N most recent entry days")
    ap.add_argument("--basis", choices=["auto", "3d", "session"], default="auto")
    ap.add_argument(
        "--winner", choices=["touched_20", "touched_40", "mfe"], default="touched_20"
    )
    ap.add_argument("--threshold", type=float, default=0.20, help="for --winner mfe")
    a = ap.parse_args()

    rows = load(a.days)
    scored = []
    for r in rows:
        o = outcome(r, a.basis)
        if o:
            scored.append((r, o, is_winner(o, a.winner, a.threshold)))

    days = sorted({r.get("entry_day") for r in rows if r.get("entry_day")})
    n_win = sum(1 for _, _, w in scored if w)
    n_scored = len(scored)

    print("=" * 72)
    print(f"EDGE — what separates winners in the pool  (winner = {a.winner}"
          + (f" >= {a.threshold:.0%}" if a.winner == "mfe" else "") + ")")
    print("=" * 72)
    print(f"rows in log      {len(rows)}")
    print(f"rows scored      {n_scored}   (basis: {a.basis})")
    print(f"entry days       {len(days)}"
          + (f"   {days[0]} .. {days[-1]}" if days else ""))
    print(f"winners          {n_win}"
          + (f"   ({n_win/n_scored:.0%} base rate)" if n_scored else ""))

    underpowered = (
        n_scored < MIN_SCORED or len(days) < MIN_DAYS or n_win < MIN_WINNERS
    )
    if underpowered:
        print()
        print("!" * 72)
        print("!! UNDERPOWERED — DO NOT CHANGE A LEVER ON THIS OUTPUT")
        short = []
        if n_scored < MIN_SCORED:
            short.append(f"scored rows {n_scored}/{MIN_SCORED}")
        if len(days) < MIN_DAYS:
            short.append(f"days {len(days)}/{MIN_DAYS}")
        if n_win < MIN_WINNERS:
            short.append(f"winners {n_win}/{MIN_WINNERS}")
        print("!! short on: " + ", ".join(short))
        print("!! Numbers below are printed so the pipeline is exercised daily and the")
        print("!! shortfall stays visible. At this N every interval will span 0.50.")
        print("!" * 72)

    if not n_scored:
        print("\nNothing scored yet. Run /review after the close.")
        return

    # --- Does our own funnel add value over the pool it drew from? ------------
    print("\n" + "-" * 72)
    print("FUNNEL VALUE — win rate by the furthest stage each name reached")
    print("-" * 72)
    print(f"{'stage':<12}{'n':>6}{'winners':>9}{'win rate':>11}{'mean MFE':>11}")
    by_stage = defaultdict(list)
    for r, o, w in scored:
        by_stage[r.get("funnel_stage", "?")].append((o, w))
    for st in STAGE_ORDER + sorted(set(by_stage) - set(STAGE_ORDER)):
        if st not in by_stage:
            continue
        items = by_stage[st]
        wins = sum(1 for _, w in items if w)
        mfes = [o["mfe_pct"] for o, _ in items if o.get("mfe_pct") is not None]
        print(f"{st:<12}{len(items):>6}{wins:>9}{wins/len(items):>10.0%}"
              f"{fmt(mean(mfes), pct=True):>11}")
    print("\nRead: if 'shortlist' and 'candidate' do not beat 'pool', the selection")
    print("step is not yet earning its keep — that is the number to move.")

    # --- Which scan feature actually separates winners? ----------------------
    print("\n" + "-" * 72)
    print("FEATURE SEPARATION — AUC 0.50 means the feature tells you nothing")
    print("-" * 72)
    print(f"{'feature':<18}{'AUC':>7}{'95% CI':>16}{'demeaned':>10}{'win mean':>10}"
          f"{'rest mean':>11}  verdict")
    for f in FEATURES:
        usable = [(r, w) for r, _, w in scored
                  if isinstance(r.get("scan"), dict)
                  and isinstance(r["scan"].get(f), (int, float))]
        pos = [r["scan"][f] for r, w in usable if w]
        neg = [r["scan"][f] for r, w in usable if not w]
        res = auc_with_ci(pos, neg)
        if not res:
            print(f"{f:<18}{'n/a':>7}{'':>16}{'':>10}{'':>10}{'':>11}  no data")
            continue
        auc, lo, hi = res

        # DAY-DEMEANED AUC. Subtract each entry day's own pool mean before ranking, so the
        # comparison is within-day only. Adopted 2026-08-05 at the engine's request after
        # it refuted two of our findings: on 5 days that shared one regime we read
        # catalyst_score at 0.376 and ATR at 0.391, and both were day-COMPOSITION effects
        # (high-catalyst pools happened to be low-base-rate days). Demeaned, they are 0.499.
        # Per-day sign checks cannot catch this when most days share a regime; demeaning can.
        # If demeaning kills the signal, you measured the tape, not the contract.
        dmean = {}
        for d in {r["entry_day"] for r, _ in usable}:
            vals = [r["scan"][f] for r, _ in usable if r["entry_day"] == d]
            dmean[d] = sum(vals) / len(vals)
        dpos = [r["scan"][f] - dmean[r["entry_day"]] for r, w in usable if w]
        dneg = [r["scan"][f] - dmean[r["entry_day"]] for r, w in usable if not w]
        dres = auc_with_ci(dpos, dneg)
        dtxt = f"{dres[0]:.3f}" if dres else "—"

        crosses = lo <= 0.5 <= hi
        # A signal that dies on demeaning is a day effect, whatever the pooled CI says.
        if dres and abs(dres[0] - 0.5) < 0.02 <= abs(auc - 0.5):
            crosses = True
        if underpowered:
            # An interval that excludes 0.50 on a handful of rows is noise, not a
            # finding. Suppress the verdict here rather than only in the header —
            # this column is where the wrong conclusion would get drawn.
            verdict = "underpowered"
        elif crosses:
            verdict = "no signal at this N"
        else:
            verdict = "HIGHER in winners" if auc > 0.5 else "LOWER in winners"
        print(f"{f:<18}{auc:>7.3f}{f'[{lo:.2f},{hi:.2f}]':>16}{dtxt:>10}"
              f"{fmt(mean(pos)):>10}{fmt(mean(neg)):>11}  {verdict}")

    print("\nEvery interval spanning 0.50 is the expected result until the sample")
    print("matures. Report that as 'no signal yet', never as 'feature X does not work'.")
    print("\nRead the `demeaned` column FIRST. It removes each entry day's pool mean, so it")
    print("compares contracts only against others screened the same morning. A pooled AUC")
    print("that collapses to ~0.50 when demeaned is a statement about which days had good")
    print("tape, not about which contracts were worth buying — and it will not survive")
    print("contact with a different regime. This check exists because we shipped two such")
    print("findings on 2026-08-05 and the engine refuted both at 74 days (F-003).")


if __name__ == "__main__":
    main()
