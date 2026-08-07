Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: 3-day hold era labels (option PnL); quintile study
Source: GammaRips recommended_oi quintiles study (2026-06-04 gate removal)
Date: 2026-07-06

# Open interest is not a quality signal — and it's stale anyway

Two independent problems:
1. **Falsified as selection quality:** `recommended_oi` quintiles were the *monotonic
   loser* — higher OI, worse realized option PnL. OI-based quality gates choked real
   winners and were removed from the engine (2026-06-04).
2. **The data is session-frozen:** pool OI/volume are scan-time snapshots; the overnight
   sweep only becomes OI the next morning. What you read in the pool is not what's true
   at entry.

Application: OI/volume matter for **fills** (can I get in and out?), never for **which
contract is good**. Keep the concerns separate in every thesis: selection cites edges;
liquidity is a fill-risk note with its own doctrine rule.

## Amendment 2026-07-28 — OI is not useless for TRADEABILITY, it is just not a gate

The falsification above stands **for quality**, unchanged. A separate 15-day engine study
(N=750) corrected an over-broad harness claim that OI is "close to unrelated" to
tradeability:

- OI **does** carry liquidity rank signal: Spearman **+0.48**, correct direction 15/15
  days.
- But as a threshold it fails: **OI ≥1000 still leaves 23.9%** of contracts under-50
  contracts on entry day. Counter-examples both ways on 2026-07-28 — STUB 3,389 OI / 1
  contract traded; HIMS 359 OI / 230 traded.
- The engine's own bug was **saturation**: the picker's OI score maxed at OI=200, so 87%
  of the pool scored perfectly liquid and 16% of those were ghosts.

Revised rule: **never use OI alone, and never with a low ceiling. Prints beat OI always.**
Tradeability precedence is prints > THIN flag > OI level (tiebreak only) —
see [[contract-tradeability-early-prints]].
