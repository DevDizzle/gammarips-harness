---
name: trade
description: The morning consult — pull the pool, screen everything for tradeability, and bring the operator a short ranked list (or a reasoned no-trade) with honest numbers. The operator decides; the agent never places or simulates an order on its own.
---

# trade

Bring the operator the best two or three things they could do today, with honest numbers,
and say which one you'd take and why. **No-trade is a valid, successful output** — the
doctrine's default answer is "no" — but it is a conclusion you reach from the data, never
a default you fall back on. `docs/TRADING-DOCTRINE.md` binds.

All decision-time data comes through the gammarips MCP (CLAUDE.md non-negotiable #1).
Anything it can't answer: note the gap, decide without it or no-trade, move on.

## 1. Gather (one pass, in parallel where you can)

- `get_market_calendar_status` — keep the ET stamp; it travels with everything.
- `get_regime_context` — `regime_rail_pass = false` (VIX > VIX3M, backwardation) is
  doctrine hard exclusion #2: fail-closed, no new position today. Note it lags the live
  pool by 1-2 sessions.
- `get_pool` view="enriched" (primary) and view="raw" (context) for the latest scan_date.
  A stale scan_date is an outage (see OPERATIONS), not a pool.
- `get_daily_report` — editorial color, never signal.

## 2. Screen for tradeability FIRST — this is the step that protects the money

**Timing floor: never read liquidity before 09:52 ET.** The feed is 15-minute delayed;
the first usable snapshot is ~09:52 (prints through ~09:37). An earlier read served as
decision-time state is a self-inflicted outage.

One batched `get_liquidity` over the whole pool (omit the singular `contract` arg).
Then, per contract:

- **Check `day.last_updated` on every row.** A bar whose date is not today is the prior
  session's bar — its `day_volume` is YESTERDAY's total masquerading as this morning's
  prints. A stale bar is a zero-print row in disguise; open interest proves nothing.
- **Grade on early prints** ([[contract-tradeability-early-prints]], proven-on-cohort,
  N=750 / 15 entry days):

  | Prints by 09:52 | Finished the day ≥50 contracts | Disposition |
  |---|---|---|
  | ≥ 20 | 100% (N=133) | liquidity-confirmed |
  | ≥ 5 | 96.3% (N=218) | liquidity-confirmed |
  | 1-4 | — | re-read at 09:55-10:00 before committing |
  | 0 | 68.1% finished under 50; 40.6% ghost | **veto-grade caution** |

- **Precedence: prints > THIN flag > OI level.** OI is a tiebreak, never a gate — OI
  ≥1,000 still leaves 23.9% of contracts under 50 on entry day
  ([[oi-not-quality-signal]]).
- **The book is invisible on this data plan.** The MCP serves no bid/ask/spread. If you
  have your own quote source (a broker screen counts), gate on **spread ≤ ~10% of mark**
  and read **dollar depth on the bid** (`bid_size × price × 100` — what you can get OUT
  of) before calling a name takeable at size. Without one, an unverifiable book is
  doctrine hard exclusion #3: accept and document the risk explicitly, or pass. Never
  silently assume.

Say how many names each check dropped and why — the counts are themselves the finding,
and they belong in the funnel rows.

## 3. Shortlist and rank — what the evidence actually supports

- **Falsified on cohort — never filter or rank on these:** moneyness
  ([[moneyness-10-15-otm]]), V/OI ([[voi-ratio-anti-edge]]), OI level
  ([[oi-not-quality-signal]]), recent option winners ([[ride-winners-mean-reverts]]).
  Report them as descriptive context only.
- **Live delta, not scan delta** — refresh via the liquidity read; 0.20-0.46 is a sanity
  check, not a gate ([[delta-band-0-20-0-46]], non-binding under the current pool).
- **Tilts, cited with their tags, never gates:** [[catalyst-mid-band]]
  (fragile-conditional); [[mom-60-conditional-lever]] ONLY when a multi-day hold is on
  the table (exit-context discipline).
- **Contract price drift:** if the contract has already re-priced far above its
  scan/overnight reference, the entry the setup was scanned at no longer exists — worse
  entry, worse RR. Note it; judgment decides.
- **Earnings — hard exclusion #1, fail-closed:** `get_signal(view="earnings")` per
  candidate; test the print date against your **intended hold window**, not the expiry
  (the flag is expiry-anchored and over-excludes short holds). `not_covered_by_plan` or
  an ambiguous date = treat as in-window and drop, flagged `earnings: unverified`.
- **Per-ticker history** where survivors are close: `query_outcomes` labels/surface for
  the name — and **filter rows carrying `illiquid_exit=true`** before concluding
  anything; sim PnL on ghost rows was never realizable.
- **Never gate on contract cost.** Cost is reported against the operator's stated paper
  book; it is not a rank input. The operator sizes.

## 4. Design the exit before entry

The exit is where the PnL lives ([[fixed-exit-composites-negative]]): the pool's
opportunity is real, and every uniform fixed exit tested is negative pool-wide.

1. Choose the intended hold first (same-day vs multi-day) — it decides admissible levers
   and the time-stop.
2. Evidence: `query_outcomes(view="surface")` for comparable contracts;
   `view="exit_rule"` for 2-3 candidate brackets; `view="harvest"` for touch
   probabilities. Report the honest base rates (stops touch more often than targets
   pool-wide).
3. Design target, stop, and a **mandatory time-stop** for THIS contract, and say why
   these levels. Where the evidence can't discriminate, say so and decide on judgment —
   the tools surface evidence; they never gate, and lack of exit-validation data is
   never a reason to no-trade.

## 5. Bring it to the operator

Two or three candidates maximum, each with: contract, live mark, prints grade, OI build,
live delta, cost, and the exit design. Say which one you'd take, why, and the single
thing most likely to make you wrong. Then stop — the operator decides, places (paper or
otherwise) their own order, and reports the real fill.

## 6. Record — this is the entire write-up

- `python scripts/funnel_log.py upsert` — **one row per pool name**, stage and reason,
  including everything the tradeability screen dropped (schema in `eval/README.md`).
  Stamp `skill_version` and `regime` on every row; without the version stamp, rows from
  before and after a skill change are not comparable and `scripts/skill_eval.py` cannot
  tell whether a change helped or the tape got easier. This pre-registration — written
  before any outcome is known — is what makes the dataset honest.
- `eval/trades.jsonl` — one line, only on a real fill, recording the actual fill (from
  the broker record where one exists), never the plan.
- Gaps the MCP couldn't answer go in your gap notes and to the vendor — never work
  around one silently.
