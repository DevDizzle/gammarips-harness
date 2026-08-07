# gammarips-harness

An open-source agentic trading harness for the **GammaRips** options-flow data layer. Clone
it, point it at the GammaRips MCP with your own API key, and run a disciplined daily loop:
your agent reasons over the curated overnight unusual-options-activity pool to **one trade
candidate per day (or none)**, screens tradeability before thesis, designs its own exit,
pre-registers every decision as data, and scores the whole pool after the close. Paper-only
by default.

This is a **workflow, not a signal service.** GammaRips deliberately exposes no pick
endpoint — your agent reaches its own conclusion over the shared data. The harness is free;
the data (an MCP key) is paid.

## Quickstart

1. **Subscribe.** Get an Agent Access key at
   [gammarips.com/pricing](https://gammarips.com/pricing) ($39/mo, 7-day free trial).
2. **Create your key** at [gammarips.com/account](https://gammarips.com/account).
3. **Export it:**
   ```bash
   export GAMMARIPS_MCP_KEY="<your key>"
   ```
   `.mcp.json` reads this from the environment. Never hardcode the key.
4. **Open the repo in Claude Code** (or any MCP client that reads `.mcp.json`). The
   `gammarips` server connects over Streamable HTTP.
5. **Run the loop:**
   ```
   /trade    — morning consult: screen the pool, rank 2-3 candidates or no-trade; you decide
   /review   — after the close: score EVERY pool name, backfill the 3-day window
   /coach    — on demand: behavioral feedback with receipts from your own record
   ```
   `scripts/edge.py` and `scripts/skill_eval.py` accumulate the evidence across days and
   say — with their own sample-size warnings — whether the screen is earning its keep.

## What's in here

| Path | What |
|---|---|
| `CLAUDE.md` | agent entry point — mission, non-negotiables, the loop |
| `docs/TRADING-DOCTRINE.md` | the rules: hard exclusions, tradeability, sizing (set your own), exit discipline |
| `docs/OPERATIONS.md` | MCP connection, timing, session procedure |
| `.claude/skills/` | the procedures: trade, review, coach, wiki-distill |
| `.claude/agents/` | wiki-librarian (wiki health) |
| `wiki/` | claim-tagged knowledge notes (`findings/`, `literature/`) + registries in `_index/` |
| `eval/` | YOUR dataset — funnel log, fills, behavior ledger, findings (starts empty) |
| `scripts/` | validators (funnel_log, behavior_log, lint) + evidence (edge, skill_eval) |

## Discipline

- **Tradeability before thesis.** The screen grades every name on early prints and book
  honesty before any story is considered — an untradeable winner is not a missed trade.
- **Pre-register before outcome.** One funnel row per pool name, written before any
  outcome is known; `/review` scores all of them, including everything the screen
  dropped. That is what makes the track record honest.
- **Cite claims with their maturity tag and exit-context.** An edge is exit-conditional;
  a finding without its N is not admissible.
- **The coach never advises.** `/coach` referees your behavior against your own written
  rules with receipts from your own record. It never says buy or sell.

## Not investment advice

GammaRips is a data vendor. Everything here is educational and on a paper-trading basis
by default. Nothing in this repo is investment advice. Trade your own capital at your own
risk, and get qualified securities and tax counsel before trading real money — especially
if you publish signals you also trade.
