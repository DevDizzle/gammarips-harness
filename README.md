# gammarips-harness

An open-source agentic trading harness for the **GammaRips** options-flow data layer. Clone
it, point it at the GammaRips MCP with your own API key, and run a disciplined daily loop:
your agent reasons over the curated overnight unusual-options-activity pool to **one trade
candidate per day (or none)**, designs its own exit, and journals every decision
point-in-time. Paper-only by design.

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
5. **Run the morning loop:**
   ```
   /morning-pool  →  /select-contract  →  /exit-plan  →  /trade-journal
   ```
   The `trade-critic` subagent must PASS before a journal entry is marked `committed`.
   Run `python scripts/lint.py` after any journal or wiki change.

## What's in here

| Path | What |
|---|---|
| `CLAUDE.md` | agent entry point — mission, non-negotiables, daily loop |
| `docs/TRADING-DOCTRINE.md` | the rules: hard exclusions, sizing (set your own), exit discipline |
| `docs/OPERATIONS.md` | MCP connection, timing, session procedure |
| `.claude/skills/` | the five procedures (morning-pool, select-contract, exit-plan, trade-journal, wiki-distill) |
| `.claude/agents/` | trade-critic (adversarial pre-commit), wiki-librarian (wiki health) |
| `wiki/` | claim-tagged knowledge notes (`findings/`, `literature/`) + registries in `_index/` |
| `journal/` | one point-in-time note per decision day — your own labeled dataset (`_TEMPLATE.md` + an example) |
| `scripts/lint.py` | deterministic journal + wiki validator |

## Discipline

- **Paper only.** No broker connections. Live-capital triggers are your call — see the
  doctrine.
- **Journal before outcome.** Pre-commit sections are immutable after commit; that is what
  makes the track record honest.
- **Cite claims with their maturity tag and exit-context.** An edge is exit-conditional;
  citing it without its hold assumption fails the critic.

## Not investment advice

GammaRips is a data vendor. Everything here is educational and on a paper-trading basis.
Nothing in this repo is investment advice. Trade your own capital at your own risk, and get
qualified securities and tax counsel before trading real money — especially if you publish
signals you also trade.
