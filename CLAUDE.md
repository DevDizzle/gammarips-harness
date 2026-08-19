# gammarips-harness — Agentic Trading Harness

## Mission
An open-source trading harness you clone and run against the **GammaRips MCP** data layer.
An agent reasons over the MCP's primitives to surface **one trade candidate per day (or
none)**, designs its own exit, pre-registers every decision as data, and scores the whole
pool after the close — so the harness can prove, with its own numbers, whether its screen
beats the pool it draws from. The harness is free; the data (an MCP API key) is paid.
This is a *workflow*, not a signal service — you supply the judgment, the MCP supplies
the curated pool and the outcome history.

Everything a decision needs comes through the gammarips MCP. Subscribers should be able to
hook into that one MCP and get everything they need — this harness proves that daily.

## Non-negotiables
1. **MCP-only at decision time.** All market/engine data used in a trade decision comes
   through the gammarips MCP (`.mcp.json`). No direct database reads, no other data
   vendors. If the MCP can't answer a question, note it, decide without it (or no-trade),
   and move on — do NOT work around it. (Exceptions: `wiki/` distillation may read
   external research — knowledge curation is not decision-time data; and if you connect
   your own broker for real fills and quotes, its records are YOUR ground truth for
   fills and the book, never a pool or signal source.)
2. **Paper only by default.** No live capital until you deliberately flip that switch —
   the real-money trigger conditions live in `docs/TRADING-DOCTRINE.md` and are your
   call, never the agent's.
3. **No pick endpoint — reason to your own contract.** The GammaRips MCP deliberately
   exposes **no** pick-returning endpoint; there is nothing to copy. Two agents reasoning
   over the same pool at different times, with different objectives and risk, should
   reach different contracts. The value is *your* analysis over the shared data.
4. **Pre-register before outcome.** Every decision day writes one funnel row per pool
   name — stage reached, exclusion reason, point-in-time features — BEFORE any outcome
   is known, and `/review` scores every row after the close, including everything the
   screen dropped. Scoring only your own picks cannot tell you whether the screen works.
   `scripts/funnel_log.py` enforces shape.
5. **Claim honesty.** Every thesis cites wiki notes by name WITH their maturity tag and
   exit-context. A fragile-conditional lever is not a proven one; a number is never
   presented without what it is measured against; a finding is never presented without
   its N.

## Read-first order
1. `docs/TRADING-DOCTRINE.md` — the rules (exclusions, sizing, exit discipline)
2. `wiki/_index/FINDINGS.md` — what is known, with claim tags
3. `eval/README.md` — the dataset and its schemas

## The loop
`/trade` in the morning (consult → the operator decides) → `/review` after the close
(score every pool name, backfill T+3) → `scripts/edge.py` and `scripts/skill_eval.py`
accumulate the evidence. `/coach` on demand — and unprompted whenever an impulse
signature shows up (an order idea minutes after a loss, hold-and-hope phrasing,
sizing above your own written cap). The coach referees behavior against YOUR rules
with receipts from `eval/behavior-ledger.jsonl`; it never says buy or sell.

## Writing style — ASD-STE100 (Simplified Technical English)
All prose in this repo obeys Simplified Technical English: chat replies, docs, PRDs, PR
text, commit messages, and emails. The `ste100` skill holds the house rules and can build
a local searchable copy of the official standard. Read it before you write a document.
These core rules always apply:

- Give the answer in the first sentence. Then give the detail.
- Write short sentences: 20 words maximum in procedures, 25 in descriptions.
- Use the active voice. Write instructions in the imperative.
- Use only the simple tenses. Do not use the "-ing" form of verbs.
- Write one instruction in each sentence. Keep one topic in each paragraph, with six
  sentences maximum. Do not use a semicolon.
- Use approved words: "do" not "perform", "make sure that" not "ensure/verify", "but" not
  "however", "must" not "shall/should", "for example" not "e.g.".
- Code, SQL, identifiers, and quoted output are verbatim. STE applies to prose only.
  Trading domain terms are technical nouns: keep "delta", "theta", "spread", "open
  interest", "time-stop". Spell each one out once, at first use.

The goal is the reader's comprehension, not compliance with the standard. When the two
conflict, choose clarity and say which rule you broke. A consult is read fast, in the
morning, before the market moves — a sentence read twice is a sentence that costs money.

**The standard itself is not in this repo, by design.** ASD-STE100 is copyrighted by ASD
and may not be republished in whole or in part without their written authority. Run
`python .claude/skills/ste100/build.py` to download your own free copy and extract the
dictionary, the rules, and the word lists into a gitignored `reference/` directory.

## Layout
| Path | What |
|---|---|
| `docs/` | doctrine, operations |
| `wiki/` | llm-wiki knowledge layer (`findings/`, `literature/` + `_index/` registries) |
| `eval/` | YOUR dataset: funnel-log, trades, behavior ledger, findings (see `eval/README.md`) |
| `.claude/skills/` | procedures: trade, review, coach, wiki-distill, ste100 |
| `.claude/agents/` | wiki-librarian (wiki health) |
| `scripts/` | funnel_log, behavior_log (validators); edge, skill_eval (evidence); lint (wiki) |

## MCP
Server: **gammarips** (Streamable HTTP, `.mcp.json`; auth via `GAMMARIPS_MCP_KEY`, see
`docs/OPERATIONS.md`). Start every session with `get_market_calendar_status`. The server
publishes its own methodology playbooks (`get_playbook` lists them): `start-here`,
`daily-workflow`, `run-your-own-tournament`, `exit-lab`, `leakage-and-data-contract` —
treat them as the product's documentation and flag drift against this repo's doctrine.
