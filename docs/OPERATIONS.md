# Operations

## MCP Connection
- **Pro OAuth Endpoint:** `https://mcp.gammarips.com/pro`
- **Bearer Key Endpoint:** `https://mcp.gammarips.com/mcp` (configured in `.mcp.json`) with header:
  ```
  Authorization: Bearer gr_live_...
  ```
- **Environment Variable:** Create an API key at `https://gammarips.com/account` and export it:
  ```bash
  export GAMMARIPS_MCP_KEY="gr_live_..."
  ```
  **Never hardcode your API key in the repository.**
- **Free Anonymous Tier:** Pointing an MCP client at `https://mcp.gammarips.com/mcp` without an `Authorization` header serves the cohort preview, daily report, regime context, market calendar, and methodology playbooks. Full cohort screening (`get_pool` enriched), tradeability (`get_liquidity`), and historical MFE/MAE excursion queries (`query_outcomes`, `replay_contract`) require Pro auth.
- If the MCP is unreachable or returns stale scan data when the market is open, record a no-trade day and stop. Never substitute another options chain source for the curated cohort.

## Timing (all ET)
- The GammaRips pipeline filters ~3,500 optionable US stocks overnight down to the surviving daily cohort (`Mid >= $1.00`, `OI >= 500`, `Delta 0.22–0.48`, `DTE 10–45`, `RV/IV >= 0.85`).
- Market open is 09:30 ET; reference entry anchor is 10:00 ET. Run the morning workflow between 09:35 and 10:30 ET once early session prints have registered.
- Date semantics: `scan_date` is the session the overnight cohort was generated from; `entry_day` is the next trading session. Record both on every funnel row.

## Daily Session Procedure
1. **Morning (`/trade` — 3-Step Workflow):**
   - **Step 1 — Pull the Daily Cohort (`get_pool`):** Check `get_market_calendar_status` and `get_regime_context`, then fetch today's surviving contracts and their volatility/liquidity metrics (`rv_iv_ratio`, `open_interest`, `mid_price`, `delta`, `dte`, opportunity surfaces, and `get_liquidity` early prints).
   - **Step 2 — Layer Your Own Catalyst Search:** Optionally dispatch parallel subagents or live X/Twitter and web search (for example, Grok searching live `$TICKER` cashtag chatter, FDA/SEC filings, or unpriced catalysts) to debate and rank the surviving contracts.
   - **Step 3 — Build the Trade Plan / Execute:** Size the position, design deterministic bracket exits (target, stop, mandatory time-stop) using historical MFE/MAE excursion distributions (`query_outcomes`), pre-register every cohort row via `python scripts/funnel_log.py upsert`, and optionally route execution to your broker MCP.
2. **After the Close (`/review`):**
   - Score every cohort contract (`query_outcomes`, `replay_contract`), backfill the 3-day window, and run `python scripts/edge.py` + `python scripts/skill_eval.py`.
3. **Behavioral Referee (`/coach`):**
   - Run on demand or when an impulse signature appears to audit actions against `docs/TRADING-DOCTRINE.md` and `eval/behavior-ledger.jsonl`.
4. **Validation:**
   - Run `python scripts/lint.py` after any `wiki/` update; `funnel_log.py` and `behavior_log.py` validate automatically on write.
