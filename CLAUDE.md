# gammarips-harness — Agentic Trading Harness

## Mission
`gammarips-harness` is a lightweight open-source workflow harness built on top of the **GammaRips MCP** curated options dataset.

GammaRips filters ~3,500 optionable US stocks down to the daily cohort of liquid, tradable, high-edge option contracts:
- `Mid >= $1.00`
- `OI >= 500`
- `Delta 0.22–0.48`
- `DTE 10–45`
- `RV/IV >= 0.85`

The curated dataset and historical MFE/MAE excursion outcomes are served over MCP:
- **OAuth:** `https://mcp.gammarips.com/pro`
- **Bearer Key:** `https://mcp.gammarips.com/mcp` with `Authorization: Bearer gr_live_...`

This is a **workflow over a curated dataset, not a signal service.** GammaRips exposes no pick-returning endpoint. Your agent pulls the daily cohort, layers live catalyst research, and builds a deterministic trade plan.

## The 3-Step Agent Workflow

1. **Pull the Daily Cohort (`get_pool`):**
   Fetch today's surviving tradable option contracts and their point-in-time volatility and liquidity metrics (`rv_iv_ratio`, `open_interest`, `mid_price`, `delta`, `dte`, opportunity surfaces), alongside `get_market_calendar_status` and `get_regime_context`.
2. **Layer Your Own Catalyst Search (Bring Your Own X / Web Agent):**
   Optionally spin up parallel subagents or live X/Twitter and web search (for example, Grok searching live `$TICKER` cashtag chatter, SEC/FDA regulatory filings, or unpriced catalysts) across Claude Code, Grok, Codex, or Cursor to debate and rank the surviving contracts.
3. **Build the Trade Plan / Execute:**
   Size the position against your risk budget, set deterministic bracket exits (target, stop, and mandatory time-stop) using historical MFE/MAE excursion data (`query_outcomes`, `replay_contract`), pre-register the decision via `scripts/funnel_log.py`, and optionally route execution to your own broker MCP.

## Core Rules
1. **Cohort-anchored universe.** Every option candidate starts from the GammaRips MCP daily cohort (`get_pool`). External agents and web/X search are used to research catalysts, verify filings, and rank surviving cohort names — never to invent off-cohort option contracts.
2. **Paper by default.** Do not route live capital until the operator explicitly flips that switch (`docs/TRADING-DOCTRINE.md`).
3. **Deterministic exits before entry.** Every trade plan specifies a target, stop loss, and mandatory time-stop calibrated with `query_outcomes` before any order is placed.
4. **Pre-register before outcome.** Write one funnel row per cohort name (`scripts/funnel_log.py`) before outcomes are known, and score every row after the close in `/review` so `scripts/edge.py` and `scripts/skill_eval.py` can measure whether selection beats the baseline cohort.
5. **Claim honesty.** Cite `wiki/` notes with their maturity tag, sample size `N`, and exit context.

## Read-First Order
1. `docs/TRADING-DOCTRINE.md` — hard exclusions, sizing, and exit discipline
2. `docs/OPERATIONS.md` — MCP endpoints, timing, and daily loop operations
3. `eval/README.md` — local evaluation dataset and schemas

## Daily Skills
- `/trade` — run the 3-step morning workflow (pull cohort → layer catalyst search → build deterministic exit plan and pre-register)
- `/review` — score every cohort contract after the close (`query_outcomes` / `replay_contract`) and update `scripts/edge.py` + `scripts/skill_eval.py`
- `/coach` — behavioral referee against your written rules in `docs/TRADING-DOCTRINE.md` using `eval/behavior-ledger.jsonl`

## Writing Style — ASD-STE100 (Simplified Technical English)
Keep prose clear, direct, and concise:
- Put the conclusion or action in the first sentence.
- Use active voice and short sentences.
- Spell out domain terms (`delta`, `theta`, `spread`, `open interest`, `time-stop`) clearly when introducing rules.

## Layout
| Path | Purpose |
|---|---|
| `docs/` | Trading doctrine and operational guide |
| `wiki/` | Claim-tagged research notes (`findings/`, `literature/`, `_index/`) |
| `eval/` | Local evaluation dataset: `funnel-log.jsonl`, `trades.jsonl`, `behavior-ledger.jsonl` |
| `.claude/skills/` | Agent workflows: `trade`, `review`, `coach`, `wiki-distill`, `ste100` |
| `.claude/agents/` | `wiki-librarian` agent |
| `scripts/` | Validators (`funnel_log.py`, `behavior_log.py`, `lint.py`) and evaluators (`edge.py`, `skill_eval.py`) |

## MCP Connection
Configured in `.mcp.json` via Streamable HTTP (`https://mcp.gammarips.com/mcp` with `Authorization: Bearer ${GAMMARIPS_MCP_KEY}` for `gr_live_...` keys, or `https://mcp.gammarips.com/pro` via OAuth). Start every session with `get_market_calendar_status`.
