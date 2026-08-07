# Findings Registry

One line per note. Format: wikilink — tag — one-line claim.

## Findings (tested on our cohorts)
- [[bullish-direction-asymmetry]] — proven-on-cohort — bullish signals carry the EV; bearish destroyed it (+4.11 vs −7.71 per trade, 3-day era)
- [[delta-band-0-20-0-46]] — proven-on-cohort — mid |delta| 0.20–0.46 separated winners historically; NON-BINDING under V7.1 (whole pool in-band since ~2026-06) — not a within-pool selector
- [[option-pnl-not-underlying]] — proven-on-cohort — evaluate on option PnL, never underlying direction (54% vs 41% on the same pool)
- [[fixed-exit-composites-negative]] — proven-on-cohort — the whole pool under any fixed exit is negative; the opportunity is real, the exit is the free variable
- [[pool-delta-calibrated]] — proven-on-cohort — pool contracts expire ITM at the delta-implied rate (41.3% vs 42.1%, N=2,146): zero directional alpha; all ROI lives in the trading layer
- [[path-calibrated-giveback]] — proven-on-cohort — excursion peaks match entry IV (50.95th pctile) and arrive LATE (median day 7/10); the verified edge surface is the GIVEBACK (median winner keeps 31% of its peak; 48.5% of ever-profitable die at a loss)
- [[three-day-harvest-curve]] — proven-on-cohort — P(touch +20% in 3d)=51%, pops land day 2–3 not day 1, fixed targets are EV-negative pool-wide, −30% touched on half of paths; tournament picks = the one positive-EV lead (N=24, unproven)
- [[mom-60-conditional-lever]] — fragile-conditional — 60-day momentum ≥ +0.35 × delta band works ONLY on a multi-day hold; zero edge same-day
- [[moneyness-10-15-otm]] — falsified-on-cohort — the 10–15% bucket did not replicate (n=1,806 re-derivation 2026-07-17; halves flip, underperforms pool); moneyness is descriptive only — never filters or ranks (your call)
- [[catalyst-mid-band]] — fragile-conditional — catalyst_score 0.5–0.8 is the only band positive in both split halves (n=467 of 1,806); high band ≥0.8 underperforms; tilt only, never a gate
- [[voi-ratio-anti-edge]] — falsified-on-cohort — V/OI > 2 filters remove winners
- [[contract-tradeability-early-prints]] — proven-on-cohort — ~43% of pool contracts are untradeable on entry day; prints by 09:52 ET is the only reliable predictor (0 prints → 68% finish under-50); precedence prints > THIN > OI
- [[oi-not-quality-signal]] — falsified-on-cohort — higher OI monotonically WORSE for quality; amended 2026-07-28: OI DOES rank tradeability (Spearman +0.48) but ≥1000 still leaves 23.9% under-50 — never a gate
- [[ride-winners-mean-reverts]] — falsified-on-cohort — recent option-winner persistence is an anti-edge
- [[entry-1000-et]] — policy-adopted — enter ~10:00 ET, not at the open
- [[regime-rail-vix-term]] — policy-adopted — VIX > VIX3M (backwardation) = fail-closed, no new positions
- [[split-adjustment-epoch-mismatch]] — policy-adopted — frozen strikes vs adjusted closes silently fabricate -100% for post-scan splits; detect by split membership, never by value; split-affected OCC bar series truncate silently

## Literature (not tested on our data)
- [[earnings-iv-crush]] — literature-established — never hold long single-leg options through earnings
- [[position-sizing-basics]] — literature-established — fixed-fractional small risk per trade; Kelly overbets on fat-tailed option outcomes
