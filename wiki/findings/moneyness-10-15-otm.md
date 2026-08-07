Status: active
Type: finding
Tag: falsified-on-cohort
Exit-context: 3-day hold era labels (option PnL)
Source: the GammaRips engine research digest (moneyness study; H17 cap widening 2026-06-02); RETAGGED by the 2026-07-17 lever-court re-derivation (harness study, `query_outcomes` labels)
Date: 2026-07-06 (retagged 2026-07-17)

# 10–15% OTM was the best moneyness bucket — DID NOT REPLICATE

Original claim (engine digest, smaller/older cohort): moneyness ~10–15% OTM outperformed
nearer and deeper buckets on realized option PnL.

**Re-derivation 2026-07-17 (lever court): FALSIFIED as a standalone selector.** On 1,806
labeled 3d rows (scans 2026-04-13 → 2026-06-26, legacy +80/−60 bracket, dedup across
chunked `query_outcomes` pulls):
- The 10–15% bucket (any catalyst): win 41%, avg −3.2% vs whole pool 42% / −1.9% — no
  outperformance, and the split-half test FLIPS sign (first half +6.3%, second half
  −9.8%). No replication.
- Catalyst-controlled (catalyst_score ≥ 0.65), the four moneyness cells (0–5 / 5–10 /
  10–15 / >15) cluster within noise on win rate (39–42%) and avg (−5.3 to −0.5), with
  every cell's halves flipping except 0–5% (stably negative). Moneyness does not
  survive as an independent lever after catalyst control.
- Same-cohort context: [[pool-delta-calibrated]] (no directional alpha) and the
  2026-07-17 finding that the delta band is non-binding under V7.1 — within-pool
  selection variance is small across ALL studied features.

Application now: moneyness is **descriptive context only — it never filters or ranks a
candidate at any stage** (operator doctrine 2026-07-17, superseding the same evening's
interim 0–15% swath). Never cite this note as a selection lever. The
original bucket claim came from a different, smaller cohort; its non-replication is the
finding. Multiple-comparisons honesty: the re-derivation tested ~20 cells; treat any
surviving pocket ([[catalyst-mid-band]]) as fragile until it survives new data.
