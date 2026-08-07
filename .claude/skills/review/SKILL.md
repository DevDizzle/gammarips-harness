---
name: review
description: After the close — score EVERY pool name against the 10:00 ET anchor, find what would have surfaced the day's winners, and backfill the 3-day window. Mechanical only; this skill never changes a lever. Run after ~16:15 ET on every decision day.
---

# review

The point is not to record what happened. It is to find the thing that would have put
today's winners on this morning's list — and to check whether the screen beat the pool
it drew from. Output is DATA: funnel rows and, rarely, a FINDINGS entry. Lever opinions
are forbidden here — one day's winners are noise; proposals go through the ledger with
pre-registered hypotheses and operator sign-off.

All data via the gammarips MCP only.

## 1. Outcomes on every pool name, not just yours

1. One batched `get_liquidity` returns each pool contract's day bar. Rows whose
   `day.last_updated` is not today are excluded AND counted — never dropped silently.
2. For names that traded meaningfully, `replay_contract` (minute, today): its `anchor`
   (close of the first bar at/after 10:00 ET) is the honest entry reference. Compute
   post-anchor MFE%, MAE%, close%, and target/stop touches from the bars — never from
   the day bar alone (the day high can predate 10:00). Honesty caveats carried verbatim:
   delayed tape, `session_complete`, thin-tape (no bar = no prints that minute; touches
   are evidence, not ticks).
3. Take session volume from `get_liquidity`'s `day_volume`, never by summing bars (bars
   can duplicate on some contracts).
4. **Sub-$0.50 contracts get flagged** — a lowball print can fake +200%; never let one
   top the table unflagged. Contracts with a handful of prints all session get
   `status: unlabeled_illiquid` — there is no honest anchor for a tape that never
   printed, and they are never counted as missed winners.
5. Upsert `outcome_session` onto **every row of today's funnel** via
   `python scripts/funnel_log.py upsert`. A log of only your own picks cannot answer
   the question this skill exists for — the regret data lives in the passed-over rows.

## 2. Did the screen earn its keep today?

Rank the pool by the 10:00-anchored move, then answer plainly:

- **Did the ranked list contain today's winners?** If not, what separated them from
  what was brought forward?
- **Did the tradeability screen throw away a winner?** Check every dropped name. If a
  "winner" won on a tape of single-lot prints, the screen was right and the winner was
  never enterable — say that explicitly instead of counting it as a miss. Record both
  sides: winners the gates dropped AND losers they avoided.

Then run `python scripts/edge.py` — it asks the same question across every accumulated
day and reports when N is too small to conclude anything. **Believe it over the day's
narrative**, and read its day-demeaned column before its pooled one.

## 3. Backfill — T+3 is where the money is

Winners peak overwhelmingly AFTER the entry session ([[three-day-harvest-curve]],
[[path-calibrated-giveback]]), so `outcome_3d` is the column that matches a real hold.

- Cheap path: `query_outcomes(view="surface", scan_date=...)` — it fills on a lag (the
  window's last session must be strictly before today, so the newest filled scan_date is
  ~4 trading days back; `WINDOW_OPEN` inside that frontier is normal, not a fault).
- Fallback when the surface can't serve a day:
  `replay_contract(granularity="day", from_date=entry_day, to_date=entry_day+2 sessions)`
  — ~3 bars per contract, a whole pool is ~50 light calls. Compute 3-day MFE/MAE against
  the **anchor already stored on `outcome_session`**, never against the day open. Bar
  highs/lows are touch ceilings, not fills.
- Rows the surface can't serve and whose anchor is missing get `status: unlabeled`;
  sub-floor tapes get `unlabeled_illiquid`. Both tails are non-random — keep them
  visible, never fake-score them.

Then `python scripts/skill_eval.py` — the per-rule scorecard: does each
`exclusion_reason` earn its keep, weighting losers-avoided equally with winners-dropped?
Proposals go to the operator through your skill ledger; **this skill never edits a rule.**

## 4. Findings

Append to `eval/FINDINGS.md` only when the accumulated evidence moves, or when a process
failure cost a real decision. Each entry: date, observation with numbers, what it implies
for `/trade`, and the current N. **Most days add nothing, and that is the correct
output.**

## Never

- Change, propose inline, or "just this once" adjust any lever or doctrine rule.
- Score against a fixed bracket as though it were your exit
  ([[fixed-exit-composites-negative]]).
- Count a winner that traded a handful of contracts as an opportunity missed.
- Fetch any non-MCP market data or external pick.
