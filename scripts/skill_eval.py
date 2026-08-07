#!/usr/bin/env python3
"""skill_eval.py — does the /trade skill's rule set earn its keep?

`edge.py` asks whether any FEATURE separates winners. This asks a different question:
whether each RULE in the skill is a good trade. `exclusion_reason` is the skill's rule set
serialized — every name we drop is stamped with the rule that dropped it — so each reason
gets a confusion matrix against what actually happened.

                won            lost
    kept    true positive   false positive
    dropped FALSE NEGATIVE  true negative      <- the rule cost / saved money

The asymmetry this script exists to defeat: dropped winners are visible and painful,
losers-you-never-bought are invisible counterfactuals. Read only the FN column and every
gate loosens over time — starting with liquidity, the rule with the most money behind it.
So TN is printed with equal weight on every line, and no rule is scored on FN alone.

Two guards on the FN count:
  * ENTERABLE ONLY. A "winner" that printed 8 contracts all session was never a trade we
    could have made. Counting it as a miss teaches the loop to loosen the one gate that
    has been saving money. Ungated FN is printed alongside so the filter's effect is
    visible, never hidden.
  * DAY-CLUSTERED. 50 rows from one session are not 50 observations — same regime, same
    tape, same rotation. 2026-07-31 is the proof: 50 rows, one decision, N=1. Every rule
    reports n_days, and the power gate counts days, not rows.

Usage:
  python scripts/skill_eval.py [--days N] [--min-bars N] [--min-volume N]
"""
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

LOG = Path(__file__).resolve().parent.parent / "eval" / "funnel-log.jsonl"

# A name reaching either of these stages was brought to the operator as a live option.
KEPT_STAGES = {"candidate", "entered"}

# Enterability floors for counting a dropped winner as a real miss.
MIN_BARS = 20         # minute bars with prints — a tape you could work an order into
MIN_VOLUME = 100      # session contracts — someone else was trading it too

# Power floors. Days, not rows: within-day rows are heavily correlated.
FLOOR_DAYS = 10
FLOOR_SCORED = 150
FLOOR_WINNERS = 20

# Rules that are NOT skill logic and cannot be improved by editing the skill.
# `regime` is a policy-adopted external rail.
NON_SKILL_RULES = {"regime"}

# Retired 2026-08-05. `sizing` (the per-trade price cap) was removed from the screen after
# the funnel measured what it cost: 12 enterable winners dropped in one session against 4
# losers avoided, and because expensive contracts on mega-caps are the LIQUID ones, the cap
# was steering the shortlist into thin tape. Historical rows keep the reason so the old days
# still validate and still score; no new row should ever carry it.
RETIRED_RULES = {"sizing"}


def load(days_back=None):
    if not LOG.exists():
        sys.exit(f"no log at {LOG}")
    rows = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
    if days_back:
        cutoff = (date.today() - timedelta(days=days_back)).isoformat()
        rows = [r for r in rows if r["entry_day"] >= cutoff]
    return rows


def outcome(row):
    """Prefer the 3-day window; fall back to the session. Returns (block, basis) or None.

    Keys on `touched_20`, not `mfe_pct`: touched_20 is the winner definition and is exact
    (server-side first-crossing off the 10:00 anchor), whereas mfe_pct on the 10:00-anchored
    rows is an explicit UPPER BOUND — the session high may have printed before the anchor.
    Rows carrying an explicit `status` (e.g. unlabeled_illiquid) are not scored.
    """
    for block, basis in (("outcome_3d", "3d"), ("outcome_session", "session")):
        o = row.get(block)
        if isinstance(o, dict) and o.get("status") is None and o.get("touched_20") is not None:
            return o, basis
    return None, None


# Rows scored off the day OHLC bar carry bars=1 (one DAY bar) and are anchored on the
# 09:30 open, not the 10:00 entry — the documented anchor defect. `bars` therefore means
# different things depending on basis, and must never be read as a minute-print count
# unless the basis says so.
DAY_BASIS = "day_ohlc_open_to_close"


def enterable(o):
    """Could we actually have worked an order into this tape?

    BOTH gates when both are observable: session volume AND minute-bar coverage. Volume
    alone is not enough — AMGN on 2026-08-04 traded 158 contracts across ELEVEN minute
    bars (one 136-lot block plus ten 1-lots) and "won" +43.6%. Counting that as a winner
    the screen missed would teach the loop to loosen the liquidity gate on exactly the
    kind of tape that gate exists to reject. Volume says someone traded; bars say you
    could have.

    `bars` is only a minute count on minute-basis rows — day-OHLC rows carry bars=1
    meaning one DAY bar, so the bar gate is skipped there and volume decides alone.
    """
    vol = o.get("day_volume")
    bars = o.get("bars")
    bars_usable = bars is not None and o.get("basis") != DAY_BASIS

    if vol is None and not bars_usable:
        return False                      # no evidence -> not credited as a miss
    if vol is not None and vol < MIN_VOLUME:
        return False
    if bars_usable and bars < MIN_BARS:
        return False
    return True


def pct(n, d):
    return f"{100*n/d:.0f}%" if d else "—"


def main(days_back, verbose):
    rows = load(days_back)
    scored, bases = [], set()
    for r in rows:
        o, basis = outcome(r)
        if o is None:
            continue
        r["_o"] = o
        r["_win"] = bool(o.get("touched_20"))
        r["_enterable"] = enterable(o)
        scored.append(r)
        bases.add(basis)

    days = sorted({r["entry_day"] for r in scored})
    winners = [r for r in scored if r["_win"]]

    print("=" * 74)
    print("SKILL EVAL — does each rule in /trade earn its keep?")
    print("=" * 74)
    print(f"rows in log      {len(rows)}")
    print(f"rows scored      {len(scored)}   (basis: {'+'.join(sorted(bases)) or 'none'})")
    print(f"entry days       {len(days)}   {days[0] + ' .. ' + days[-1] if days else ''}")
    print(f"winners          {len(winners)}   ({pct(len(winners), len(scored))} base rate)")
    print(f"enterable filter volume>={MIN_VOLUME} (or minute bars>={MIN_BARS} where volume absent)")

    if not scored:
        print("\nNothing scored. Run /review to populate outcomes before asking this question.")
        return

    # ---- anchor provenance ------------------------------------------------------------
    # The caveat belongs where the wrong conclusion gets drawn, so it prints before any
    # rule number, not in a footnote.
    defective = [r for r in scored if r["_o"].get("basis") == DAY_BASIS]
    if defective:
        print("\n" + "!" * 74)
        print(f"!! ANCHOR DEFECT — {len(defective)}/{len(scored)} scored rows are anchored on the")
        print("!! 09:30 DAY OPEN, not the 10:00 ET entry. Their mfe/mae are wrong in BOTH")
        print("!! directions (HPE 08-04: +15.1% off the day open vs +51.0% off the true")
        print("!! 10:00 anchor), so the error is noise, not a constant bias you can correct.")
        print("!! Re-score these off replay_contract before tuning any rule on them.")
        print("!" * 74)

    underpowered = (len(days) < FLOOR_DAYS or len(scored) < FLOOR_SCORED
                    or len(winners) < FLOOR_WINNERS)
    if underpowered:
        print("\n" + "!" * 74)
        print("!! UNDERPOWERED — DO NOT CHANGE A RULE ON THIS OUTPUT")
        print(f"!! short on: days {len(days)}/{FLOOR_DAYS}, "
              f"scored {len(scored)}/{FLOOR_SCORED}, winners {len(winners)}/{FLOOR_WINNERS}")
        print("!! Printed so the pipeline is exercised and the shortfall stays visible.")
        print("!" * 74)

    # ---- per-day discrimination check -------------------------------------------------
    # A day where every name got the same disposition carries no information about the
    # rules, however many rows it has. Surface that rather than letting it pad the N.
    print("\n" + "-" * 74)
    print("DAY QUALITY — a day with one disposition tells you nothing about the rules")
    print("-" * 74)
    print(f"{'day':<12}{'scored':>7}{'reasons':>9}{'kept':>6}{'winners':>9}  {'verdict'}")
    informative_days = 0
    for d in days:
        dr = [r for r in scored if r["entry_day"] == d]
        reasons = {r["exclusion_reason"] for r in dr}
        kept = sum(1 for r in dr if r["funnel_stage"] in KEPT_STAGES)
        w = sum(1 for r in dr if r["_win"])
        ok = len(reasons) > 1
        informative_days += ok
        print(f"{d:<12}{len(dr):>7}{len(reasons):>9}{kept:>6}{w:>9}  "
              f"{'ok' if ok else 'NO DISCRIMINATION — 1 reason for the whole pool'}")
    print(f"\ninformative days: {informative_days}/{len(days)}")

    # ---- rule scorecard ---------------------------------------------------------------
    print("\n" + "-" * 74)
    print("RULE SCORECARD — per exclusion_reason, what dropping on it bought and cost")
    print("-" * 74)
    print(f"{'rule':<19}{'drop':>5}{'days':>5}{'FN':>4}{'FNe':>5}{'TN':>5}"
          f"{'  kill rate':>11}{'  cost/day':>10}")

    by_rule = defaultdict(list)
    for r in scored:
        if r["funnel_stage"] not in KEPT_STAGES:
            by_rule[r["exclusion_reason"]].append(r)

    for rule in sorted(by_rule):
        grp = by_rule[rule]
        fn_all = [r for r in grp if r["_win"]]
        fn_ent = [r for r in fn_all if r["_enterable"]]
        tn = [r for r in grp if not r["_win"]]
        nd = len({r["entry_day"] for r in grp})
        tag = ("  (RETIRED 2026-08-05)" if rule in RETIRED_RULES
               else "  (not skill logic)" if rule in NON_SKILL_RULES else "")
        print(f"{rule:<19}{len(grp):>5}{nd:>5}{len(fn_all):>4}{len(fn_ent):>5}{len(tn):>5}"
              f"{pct(len(tn), len(grp)):>11}{(len(fn_ent)/nd if nd else 0):>10.2f}{tag}")

    print("\nFN  = dropped a winner (any tape)      FNe = dropped an ENTERABLE winner")
    print("TN  = dropped a loser, correctly       kill rate = TN / dropped")
    print("cost/day = enterable winners this rule threw away per informative day.")
    print("A rule with a high kill rate and a low cost/day is doing its job. Judge on both.")

    # ---- kept vs dropped, and the baselines -------------------------------------------
    kept = [r for r in scored if r["funnel_stage"] in KEPT_STAGES]
    dropped = [r for r in scored if r["funnel_stage"] not in KEPT_STAGES]
    kept_w = sum(1 for r in kept if r["_win"])
    base = len(winners) / len(scored)

    print("\n" + "-" * 74)
    print("THE SCOREBOARD — did the screen beat what it drew from?")
    print("-" * 74)
    print(f"{'cohort':<28}{'n':>5}{'winners':>9}{'win rate':>10}")
    print(f"{'kept (candidate+entered)':<28}{len(kept):>5}{kept_w:>9}{pct(kept_w, len(kept)):>10}")
    print(f"{'dropped':<28}{len(dropped):>5}"
          f"{sum(1 for r in dropped if r['_win']):>9}"
          f"{pct(sum(1 for r in dropped if r['_win']), len(dropped)):>10}")
    print(f"{'whole pool (baseline)':<28}{len(scored):>5}{len(winners):>9}{pct(len(winners), len(scored)):>10}")
    if kept:
        exp = base * len(kept)
        print(f"\nrandom draw of {len(kept)} from the pool would be expected to hold "
              f"{exp:.1f} winners; we held {kept_w}.")
        print("Edge over a random screen of the same width: "
              f"{100*(kept_w/len(kept) - base):+.1f} points.")
    print("\nIf 'kept' does not clear 'whole pool', the selection step is decoration.")

    # ---- skill version ----------------------------------------------------------------
    vers = defaultdict(list)
    for r in scored:
        vers[r.get("skill_version", "unstamped")].append(r)
    if len(vers) > 1 or "unstamped" not in vers:
        print("\n" + "-" * 74)
        print("BY SKILL VERSION — did a change to /trade actually help?")
        print("-" * 74)
        print(f"{'version':<14}{'n':>5}{'days':>6}{'winners':>9}{'win rate':>10}  base rate by day")
        for v in sorted(vers):
            g = vers[v]
            w = sum(1 for r in g if r["_win"])
            nd = len({r['entry_day'] for r in g})
            per = []
            for d in sorted({r["entry_day"] for r in g}):
                dr = [r for r in g if r["entry_day"] == d]
                per.append(f"{d[5:]} {pct(sum(1 for r in dr if r['_win']), len(dr))}")
            print(f"{v:<14}{len(g):>5}{nd:>6}{w:>9}{pct(w, len(g)):>10}  {', '.join(per)}")
        print("\nREGIME-CONFOUNDED — do NOT read this as the skill improving. The whole-pool")
        print("base rate moves with the tape, and each version here spans different days, so a")
        print("version that happens to cover a melt-up will look better than one that didn't.")
        print("Only compare versions across days with comparable pool base rates, and only")
        print("once each version has enough DAYS (not rows) to average over.")
    else:
        print("\nNo skill_version stamps yet — before/after comparison is unavailable.")

    if verbose:
        print("\n" + "-" * 74)
        print("ENTERABLE WINNERS WE DROPPED — the actual misses, most recent first")
        print("-" * 74)
        miss = sorted((r for r in dropped if r["_win"] and r["_enterable"]),
                      key=lambda r: (r["entry_day"], r["ticker"]), reverse=True)
        if not miss:
            print("none")
        for r in miss[:40]:
            o = r["_o"]
            print(f"  {r['entry_day']}  {r['ticker']:<6} {r['exclusion_reason']:<18}"
                  f" mfe {100*o['mfe_pct']:+6.1f}%  bars {o.get('bars', '?'):>4}"
                  f"  vol {o.get('day_volume', '?')}")


if __name__ == "__main__":
    a = sys.argv[1:]
    d = int(a[a.index("--days") + 1]) if "--days" in a else None
    if "--min-bars" in a:
        MIN_BARS = int(a[a.index("--min-bars") + 1])
    if "--min-volume" in a:
        MIN_VOLUME = int(a[a.index("--min-volume") + 1])
    main(d, "-v" in a or "--verbose" in a)
