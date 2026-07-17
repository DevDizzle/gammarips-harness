# gammarips-harness — Agentic Trading Harness

## Mission
An open-source trading harness you clone and run against the **GammaRips MCP** data layer.
An agent reasons over the MCP's primitives to surface **one trade candidate per day (or
none)**, designs its own exit, and journals every decision point-in-time. The harness is
free; the data (an MCP API key) is paid. This is a *workflow*, not a signal service — you
supply the judgment, the MCP supplies the curated pool and the outcome history.

Everything a decision needs comes through the gammarips MCP. Subscribers should be able to
hook into that one MCP and get everything they need — this harness proves that daily.

## Non-negotiables
1. **MCP-only at decision time.** All market/engine data used in a trade decision comes
   through the gammarips MCP (`.mcp.json`). No direct database reads, no other data
   vendors, no other MCPs. If the MCP can't answer a question, note it, decide without it
   (or no-trade), and move on — do NOT work around it. (Exception: `wiki/` distillation may
   read external research and literature — that is knowledge curation, not decision-time
   data.)
2. **Paper only.** No live capital, no broker connections by default. The real-money
   trigger conditions live in `docs/TRADING-DOCTRINE.md` and are your call, never the
   agent's.
3. **No pick endpoint — reason to your own contract.** The GammaRips MCP deliberately
   exposes **no** pick-returning endpoint; there is nothing to copy. Two agents reasoning
   over the same pool at different times, with different objectives and risk, should reach
   different contracts. The value is *your* analysis over the shared data.
4. **Journal before outcome.** Every decision — including no-trade — is journaled
   point-in-time with the planned exit, BEFORE any outcome is known. Pre-commit sections
   are never edited after commit. `scripts/lint.py` enforces shape.
5. **Claim honesty.** Every thesis cites wiki notes by name WITH their maturity tag and
   exit-context. A fragile-conditional lever is not a proven one; citing an edge without
   its hold/exit context is a critic FAIL.

## Read-first order
1. `docs/TRADING-DOCTRINE.md` — the rules (exclusions, sizing, exit discipline)
2. `wiki/_index/FINDINGS.md` — what we know, with claim tags
3. `journal/` — the two most recent entries (where we are)

## Daily loop
`/morning-pool` → `/select-contract` → `/exit-plan` → `/trade-journal` (commit) →
[T+1 or at exit] `/trade-journal` (close). The **trade-critic** subagent MUST pass before
any journal entry is marked `committed`.

## Layout
| Path | What |
|---|---|
| `docs/` | doctrine, operations |
| `wiki/` | llm-wiki knowledge layer (`findings/`, `literature/` + `_index/` registries) |
| `journal/` | one note per decision day — the harness's own labeled dataset |
| `.claude/skills/` | procedures: morning-pool, select-contract, exit-plan, trade-journal, wiki-distill |
| `.claude/agents/` | trade-critic (adversarial pre-commit), wiki-librarian (wiki health) |
| `scripts/lint.py` | deterministic journal + wiki validator — run after any journal/wiki change |

## MCP
Server: **gammarips** (Streamable HTTP, `.mcp.json`; auth via `GAMMARIPS_MCP_KEY`, see
`docs/OPERATIONS.md`). Start every session with `get_market_calendar_status`. The server
publishes its own methodology playbooks (`get_playbook` lists them): `start-here`,
`daily-workflow`, `run-your-own-tournament`, `exit-lab`, `leakage-and-data-contract` —
treat them as the product's documentation and flag drift against this repo's doctrine.
