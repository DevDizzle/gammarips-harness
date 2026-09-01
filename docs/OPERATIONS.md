# Operations

## MCP connection
- Endpoint: the GammaRips MCP over Streamable HTTP, configured in `.mcp.json`. The
  authoritative, always-current endpoint URL is published at
  `https://gammarips.com/mcp.json` — if a connection fails, copy the `url` from there.
- Auth: bearer key in env `GAMMARIPS_MCP_KEY`. Subscribe at
  `https://gammarips.com/pricing` ($29/mo founding price for the first 100
  subscribers, 30-day free trial), then create a key at
  `https://gammarips.com/account` and export it:
  ```bash
  export GAMMARIPS_MCP_KEY="<your key>"
  ```
  This harness always sends its key — dogfooding the keyed path is part of the point.
  **Never hardcode the key anywhere in this repo.**
- A free anonymous tier exists without a key (pool preview, daily reports, methodology
  playbooks, regime/calendar) — but the daily loop needs the pro tools, so a key is
  required for real use.
- If the MCP is down or erroring: that's a no-trade day. Note the outage on the day's
  funnel rows. Do not fall back to any other data source.

## Timing (all ET)
- The engine scans overnight; the enriched pool for `scan_date = D` lands early morning
  D+1. Regime + pool tools serve the latest closed scan.
- Market open 09:30. The engine's own reference entry is 10:00. The harness session runs
  best ~09:35–10:30: pool is final, regime known, and the decision still leads the day.
- Date semantics: `scan_date` is the evening the flow was detected; entry day is the next
  session. Always state both on every funnel row.

## Daily session procedure
1. `/trade` — calendar, regime, pool, tradeability screen, ranked candidates (or
   no-trade), exit design, funnel pre-registration. You decide and place any order.
2. After the close: `/review` — score every pool name, backfill the 3-day window, run
   `edge.py` + `skill_eval.py`.
3. `/coach` on demand, or unprompted when an impulse signature appears.
4. `python scripts/lint.py` after any wiki write; the funnel and behavior logs
   self-validate on upsert.

## When the MCP can't answer
If a decision-relevant question has no MCP answer, note it on the funnel row, decide without
it (or no-trade), and move on. Never improvise a data source. If you think it's a genuine
product gap, that is useful feedback to the vendor (`https://gammarips.com`).

## Outage / failure handling
Classify before acting: MCP unreachable | tool error | stale data (calendar says open but
pool is old) | auth failure. All four → record a no-trade day with the classification, stop.
Never improvise a data source.
