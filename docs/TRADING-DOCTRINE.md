# Trading Doctrine

The rules layer. Skills describe *how*; this file describes *what is never negotiable*.
Amend it deliberately — it defines the constraints the trade-critic enforces.

## Status
**PAPER by default.** Every decision is pre-registered in `eval/funnel-log.jsonl` and real
(paper) fills recorded in `eval/trades.jsonl`. No live capital until you deliberately flip
that switch (see Real-money triggers).

## Instrument universe
Single-leg long options drawn from the day's curated GammaRips pool (via the MCP). Nothing
off-pool. Bullish bias — pragmatic, not dogmatic; the engine pool is currently BULLISH-only
anyway.

## The daily decision
One candidate per day **or none**. No-trade is a first-class, recorded outcome — the
doctrine's default answer is "no."

## Hard exclusions (any one → no-trade on that candidate)
1. **Earnings in the intended hold window.** Literature-settled (IV crush,
   [[earnings-iv-crush]]). The engine's rail is applied at pick time, not in the pool —
   verify per-candidate yourself via `get_signal(view="earnings")`, testing the date
   against your **intended hold window** (not the contract expiry). An uncovered or
   ambiguous date is **fail-closed**: treat as in-window and drop the name, flagged
   `earnings: unverified` on its funnel row.
2. **Regime rail fail.** `get_regime_context` → `regime_rail_pass = false` (VIX > VIX3M)
   means fail-closed: no new position that day.
3. **Unverifiable liquidity you are not willing to own.** The MCP serves session-frozen
   OI/volume (see wiki [[oi-not-quality-signal]]). If fresh liquidity can't be verified,
   either accept and *document* the risk on the funnel row, or pass. Never silently assume.
   The early-print grade makes this objective ([[contract-tradeability-early-prints]]):
   zero prints by 09:52 ET is veto-grade caution; >=5 prints is liquidity-confirmed.
   Where you have your own quote source, a spread wider than ~10% of mark is the same
   exclusion by another door — the books in this universe are thin enough that crossing
   a wide one is the single most expensive available mistake. Never use a market order.

## Exit discipline
- The exit is designed **before** entry (inside `/trade`) and recorded with the decision.
  Target, stop, and a **mandatory time-stop** (no open-ended holds). On a real fill,
  rest the target at the broker as GTC immediately — a named target that is not a
  resting order is a wish.
- Never default to the engine's GIGO bracket out of habit — fixed exits are the documented
  value-destroyer (wiki [[fixed-exit-composites-negative]]). Consult the opportunity-surface
  evidence where it discriminates; where it doesn't, **trader judgment decides** — the
  distributional exit tools are research color, never a gate.
- **Exit evidence never vetoes.** Only the hard exclusions above can no-trade a surfaced
  candidate. Lack of exit-validation data — an untestable trailing rule, an indeterminate
  bracket comparison — is a note on the row, never a reason to pass.
- The planned exit may be revised intraday only in the risk-reducing direction (tighten
  stop, take profit earlier); every revision is logged with a timestamp.

## Sizing (paper, but practiced as if real)
- **Set your own position size.** This harness does not prescribe a lot size or a notional
  cap — those are your risk decisions. Pick a paper notional and a maximum-per-position cap
  that fit your own account and risk tolerance, and write them here before you trade.
  Every entry records the chosen size AND its rationale — size is a logged
  decision, not a constant.
- Risk framing (practice every entry): assume the full premium can go to zero, and write
  the real-capital arithmetic. On a reference book of $ACCOUNT, an X% risk budget is
  $ACCOUNT × X%; a full-size position that zeroes is a set fraction of that book — so max
  size should be a deliberate, logged, justified risk, not a default. Sizing to the planned
  stop (not to zero) is the intended way to carry larger notional without larger risk.
- Comparability: cross-day *dollar* exposure is not constant, so the track record is
  evaluated on **option PnL percent** (per Measurement), not dollars.

## Real-money triggers (your call — the agent never initiates)
Live capital should require, at minimum, ALL of: (a) a paper track record you set the bar
for (e.g. N>=30 harness paper trades with EV>=0); (b) enough manually confirmed matches to
trust the workflow; (c) securities and tax review appropriate to your jurisdiction; (d) an
explicit, deliberate decision to go live. Until then, any "we should go live" reasoning is
out of scope. **Note:** trading into a signal you also publish can create legal exposure —
get qualified counsel before charging for or publishing signals you trade.

## Measurement
- Evaluate everything on **option PnL**, never underlying direction
  (wiki [[option-pnl-not-underlying]]).
- The funnel log is the dataset: rows are pre-registered point-in-time, outcomes are
  appended after the close for EVERY pool name (the passed-over rows are where the
  regret data lives), and `scripts/edge.py` / `scripts/skill_eval.py` read the
  accumulation. That is what makes the track record honest and the go-live trigger
  meaningful.
