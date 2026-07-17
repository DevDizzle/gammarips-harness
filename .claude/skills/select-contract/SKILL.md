---
name: select-contract
description: Reason from the morning-pool shortlist to ONE candidate contract or an explicit no-trade. Runs after /morning-pool; output feeds /exit-plan and the journal.
---

# select-contract

Input: the `/morning-pool` shortlist **with its live-refresh overlay and run timestamp**.
Output: one candidate + a defensible elimination trail, or a reasoned no-trade. **No-trade
is a valid, successful output** — the doctrine's default answer is "no."

## Timing gate (check first)
Doctrine entry is ~10:00 ET ([[entry-1000-et]]). If the morning-pool run timestamp is an
afternoon run (well past the entry window), **default to no-trade** — the opportunity is
time-conditioned to a morning entry and the edge levers are calibrated there. Journal the
no-trade with the run time as the reason; an afternoon session is for review, not new
entries. Only continue below when the run is inside the entry window.

## Procedure
1. **Earnings screen (hard exclusion):** for each shortlisted ticker,
   `get_signal(view="earnings", ticker=...)` → take `next_earnings_date` and test it
   against YOUR **intended exit / hold window**, not the contract expiry.
   `earnings_in_window` is expiry-anchored, so it over-excludes a short hold — this
   harness holds intraday to ~3 days, so a print landing after the planned exit but
   before expiry is NOT a hold-through-earnings risk ([[earnings-iv-crush]]). If the tool
   returns `not_covered_by_plan` (or a null/ambiguous date), **fail closed** — treat the
   name as in-window and drop it, flagging it `earnings: unverified` in the journal. There
   is no web fallback (`web_search` was removed in MCP v4); the earnings rail is
   fail-closed by design.
2. **Head-to-head on LIVE state:** compare survivors using the morning-pool live overlay,
   NOT the scan-frozen fields:
   - **Delta band on the CURRENT delta** — the live delta must sit inside 0.20–0.46
     ([[delta-band-0-20-0-46]]); scan-time delta drifts overnight/intraday, so a name that
     qualified in the pool can be out of band now → drop it.
   - **Price now vs the overnight reference** — if the contract has already ripped from its
     scan/overnight mark, the opportunity is largely consumed (worse entry, worse RR) →
     drop it. A flat-to-modestly-lower live mark on an otherwise-valid setup is the better
     entry.
   - **OI building vs dead** — prefer contracts whose OI is building since the open over
     ones dead vs the scan snapshot, as a **liveness** read only, never a quality score
     ([[oi-not-quality-signal]], [[voi-ratio-anti-edge]] still bind — never rank on OI).
   Where survivors are still close, consult per-ticker history: `get_signal(ticker=...)`,
   `query_outcomes(view="labels", ticker=...)`, `query_outcomes(view="surface", ticker=...)`
   — how have THIS name's pool appearances resolved?
3. **Large shortlists (>8, rare):** run the server's `run-your-own-tournament` playbook
   pattern (`get_playbook`) with YOUR criteria — batches, top-2 advance, consensus. That
   pattern is a selection harness, not an oracle; the wiki levers are still the criteria.
4. **Decide:** one candidate or none. State the single strongest reason AND the single
   strongest objection (the critic will probe it anyway).

## Forbidden
- Any data source other than the gammarips MCP.
- Citing [[mom-60-conditional-lever]] for a same-day hold (exit-context mismatch).
