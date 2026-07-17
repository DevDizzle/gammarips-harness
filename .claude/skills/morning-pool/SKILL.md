---
name: morning-pool
description: Daily opening procedure — market calendar, regime rail, curated pool, and a shortlist of 3-5 candidates with doctrine levers applied. Run at the start of every trading-day session, before any selection work.
---

# morning-pool

Read `docs/TRADING-DOCTRINE.md` and the last journal entry first. All data via the
gammarips MCP only.

## Procedure
1. **Calendar + run time:** `get_market_calendar_status`. Holiday/closed → journal a
   no-trade entry and stop. **Record the current ET time it returns as the run
   timestamp** — selection is time-conditioned, not day-frozen, so this stamp travels
   with the shortlist and into the journal.
2. **Regime:** `get_regime_context` for the latest scan date. `regime_rail_pass = false` →
   journal a no-trade (regime rail, [[regime-rail-vix-term]]) and stop.
3. **Pool:** `get_pool` (view="enriched", the default — narrative) + `get_pool(view="features")`
   (quantitative) for the latest scan_date. Confirm the scan_date is the most recent
   session — a stale pool is an outage (see OPERATIONS).
4. **Context:** `get_daily_report` for the editorial read. Treat it as color, not signal.
5. **Shortlist 3–5** by the doctrine levers, citing wiki notes with tags:
   [[delta-band-0-20-0-46]] (primary), [[moneyness-10-15-otm]] (secondary),
   [[mom-60-conditional-lever]] ONLY if a multi-day hold is on the table. Never use V/OI
   or OI as quality ([[voi-ratio-anti-edge]], [[oi-not-quality-signal]]), never favor
   recent winners ([[ride-winners-mean-reverts]]). These levers read scan-frozen fields —
   the shortlist is **provisional** until the live refresh in step 6.
6. **Live refresh (decision-time state):** `get_liquidity(contracts=[...])` over the
   shortlisted contracts in ONE call (batch mode = omit the singular `contract` arg) —
   returns entry-day marks (last trade + day range), OI built
   since the open vs the scan-time snapshot, and delayed IV + greeks
   (delta/gamma/theta/vega). This is what makes two runs at different times genuinely
   differ. Overlay the live fields onto the shortlist and carry them (not the scan-frozen
   values) into select-contract; note any name whose live delta has drifted out of
   0.20–0.46 or whose OI is dead rather than building. (Bid/ask/spread is still absent on
   this data plan — a known quote-feed limitation; note it, never block on it.)
7. **Output:** a shortlist table **stamped with the run timestamp** — ticker, contract,
   scan-time delta vs LIVE delta, moneyness, scan OI vs live OI, last mark, score, one-line
   rationale. Earnings is screened per-candidate in select-contract.

If the MCP couldn't answer a decision-relevant question, note it in the journal and decide
without it (or no-trade). Never improvise a data source.
