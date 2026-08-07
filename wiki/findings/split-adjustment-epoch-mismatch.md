# Split-adjustment epoch mismatch corrupts strike-vs-underlying math silently

```
Status: active
Type: finding
Tag: policy-adopted
Exit-context: n/a (methodology / data-integrity note)
Source: GammaRips engine research note, 2026-08-07 (surfaced via the MCP data contract)
Date: 2026-08-07
```

## Claim

Any arithmetic comparing a frozen option strike against an underlying price fetched
under a different adjustment epoch is silently wrong for every ticker that split after
the contract was selected — and it fails as a *plausible value*, not as an error.
Detect exposure by **split membership** (a splits calendar filtered to
`execution_date > scan_date`, strict), never by scanning output values.

## Mechanism

Strikes are frozen at scan time in pre-split units. Adjusted daily bars restate history
for corporate actions occurring *after* the bar's date. `max(0, close - strike)` across
that mismatch collapses to zero and books a -100% that is indistinguishable from an
ordinary total loss. Raw closes do not rescue it: OCC re-issues the contract on a split,
so the stored OCC symbol and strike stop describing a live deliverable under any
convention — and the bar series for the ORIGINAL OCC symbol (including via
`replay_contract`) **truncates silently at the split date rather than erroring**.

## Evidence

Engine cohort, 2026-08-07: a 4-for-1 split contaminated 23 rows of a published
1,495-contract full-life cohort for a month; two were genuinely ITM in pre-split units
but booked as -100%. A value-based search (`return = -1.0`) would have missed a real
case reading -0.843 — membership detection found it. The engine now stops computing
(terminal status) rather than computing wrong.

## Application

- In `/review`: a `replay_contract` series that truncates mid-window, or a contract
  whose bars go dead, is a **split suspect before it is a liquidity conclusion** —
  check the split calendar before booking an outcome from it.
- Never compute moneyness, intrinsic, or breakeven from a stored strike and a freshly
  fetched close without confirming no split executed after the scan date.
- When auditing for this class of bug, enumerate the affected membership from the split
  calendar and inspect those rows; value-pattern searches declare victory early.

Related: [[fixed-exit-composites-negative]] (the life-cohort context),
[[contract-tradeability-early-prints]] (the sibling class of silently-wrong liquidity
numbers: a stale day bar serving prior-session volume as entry-day prints — always
check `day.last_updated`).
