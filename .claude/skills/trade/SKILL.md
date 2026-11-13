---
name: trade
description: Run the 3-step GammaRips morning workflow — (1) pull the curated daily cohort via get_pool, (2) layer live catalyst search via X/web subagents and screen tradeability, and (3) build a deterministic trade plan with MFE/MAE bracket exits (query_outcomes).
---

# trade

Run the 3-step morning workflow over the curated GammaRips MCP dataset and bring the operator the best two or three trade plans for the session (or a reasoned no-trade). **No-trade is a first-class output** (`docs/TRADING-DOCTRINE.md`).

All option cohort and outcome data comes through the **GammaRips MCP** (`https://mcp.gammarips.com/pro` via OAuth or `https://mcp.gammarips.com/mcp` with `Authorization: Bearer gr_live_...`).

## Step 1: Pull the Daily Cohort (`get_pool`)

GammaRips filters ~3,500 optionable US stocks down to the daily cohort of liquid, tradable, high-edge contracts (`Mid >= $1.00`, `OI >= 500`, `Delta 0.22–0.48`, `DTE 10–45`, `RV/IV >= 0.85`).

1. **Session & Regime Check:**
   - Call `get_market_calendar_status` and record the ET timestamp.
   - Call `get_regime_context`. If `regime_rail_pass = false` (VIX > VIX3M backwardation), hard exclusion #2 applies: fail-closed, no new long position today.
2. **Fetch Surviving Contracts:**
   - Call `get_pool(view="enriched")` for the latest `scan_date` to retrieve each surviving contract's point-in-time volatility and liquidity metrics (`rv_iv_ratio`, `open_interest`, `mid_price`, `delta`, `dte`, and opportunity surfaces).
   - Call `get_daily_report` for overnight macro/session context.
3. **Verify Morning Tradeability (`get_liquidity`):**
   - After 09:52 ET (15-minute delayed feed), run one batched `get_liquidity` call across the cohort.
   - Verify `day.last_updated` matches today's session date.
   - Grade early session prints ([[contract-tradeability-early-prints]]):
     - `>= 5` prints by 09:52 ET: liquidity-confirmed (96.3% finish `>= 50` contracts).
     - `1–4` prints: re-check at 09:55–10:00 ET before committing.
     - `0` prints: veto-grade caution (68.1% finish under 50 contracts).
   - If connected to a live broker quote source, require bid/ask spread `<= 10%` of mark and inspect dollar bid depth (`bid_size * price * 100`).

## Step 2: Layer Your Own Catalyst Search (Bring Your Own X / Web Agent)

With the surviving liquid contracts in hand, layer your own catalyst and narrative research to rank the shortlist:

1. **Check Earnings Hard Exclusion (`get_signal`):**
   - Call `get_signal(view="earnings")` per survivor and verify the print date against your **intended hold window** ([[earnings-iv-crush]]). Any earnings event inside the hold window — or an unverified date — drops the candidate (`exclusion_reason: "earnings"`).
2. **Dispatch Catalyst Subagents / X & Web Search (Optional):**
   - Spin up parallel subagents or live search tools (for example, Grok searching live `$TICKER` cashtag chatter on X/Twitter, SEC 8-K / Form 4 filings, FDA PDUFA calendars, or sector news) to surface unpriced catalysts and debate bull vs. bear cases on the surviving cohort tickers.
   - Keep quantitative discipline intact: do not filter or rank on falsified single-factor rules like raw OI level ([[oi-not-quality-signal]]) or volume/OI ratio ([[voi-ratio-anti-edge]]). Use `rv_iv_ratio`, live delta ([[delta-band-0-20-0-46]]), and verified catalysts to separate the top 2–3 candidates.

## Step 3: Build the Trade Plan / Execute

Every candidate requires a deterministic exit plan before entry ([[fixed-exit-composites-negative]]):

1. **Calibrate Bracket Exits with Historical MFE/MAE (`query_outcomes`):**
   - Select the intended hold horizon (same-day session vs. multi-day 3-session window, [[three-day-harvest-curve]]).
   - Query historical excursion data via `query_outcomes(view="surface")`, `query_outcomes(view="exit_rule")`, and `query_outcomes(view="harvest")` (filtering out `illiquid_exit=true` ghost rows).
   - Set a deterministic **profit target**, **stop loss**, and **mandatory time-stop** for each candidate contract.
2. **Size the Position:**
   - Size against the operator's risk budget and planned stop loss (`docs/TRADING-DOCTRINE.md`), stating the contract cost and maximum dollar risk explicitly.
3. **Pre-Register & Present (or Route to Broker MCP):**
   - Pre-register **one row per cohort contract** (including all excluded rows and their `exclusion_reason`) via `python scripts/funnel_log.py upsert` before outcomes are known.
   - Present the top 2–3 ranked trade plans (contract, `rv_iv_ratio`, live mark, early prints grade, delta, DTE, catalyst summary, and deterministic target/stop/time-stop bracket) to the operator — or, when configured by the operator, route the approved bracket order to the operator's broker MCP and log real fills in `eval/trades.jsonl`.
