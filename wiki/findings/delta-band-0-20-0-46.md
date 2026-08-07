Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: 3-day hold realized labels (1,375-trade study, option PnL)
Source: the GammaRips engine 1,375-trade realized-label study; edge-rank levers (docs/DECISIONS 2026-06-11)
Date: 2026-07-06

# Mid-delta band |delta| 0.20–0.46

Across the 1,375-trade realized-label study, **mid |delta| 0.20–0.46 was the only contract
feature that separated won from lost trades**. Deep OTM lottery strikes and near-ITM both
underperformed the band. It is the confirmed lever behind the engine's edge-rank pre-sort
(alongside RR<1.4 and ATR-move as soft tilts).

Application: prefer candidates inside the band; treat outside-band candidates as needing an
explicit reason. Interaction note: the band is also the conditioning variable that makes
[[mom-60-conditional-lever]] work at all — the levers are call-delta-defined and do not
transfer to puts.

**Scope update 2026-07-17 (lever court): NON-BINDING under the current V7.1 policy.**
The engine now delta-targets its recommended contracts, so essentially the entire pool
sits inside 0.20–0.46 — verified 2026-07-16/17: the band-filtered 30-day outcome
aggregate was IDENTICAL to the unfiltered pool (n=436=436; a narrow 0.42–0.46 test
confirmed the filter itself works). The historical claim stands on its own cohort, but
the band can no longer discriminate WITHIN the pool and must not be cited as a
within-pool selector. It remains the conditioning context for
[[mom-60-conditional-lever]] and a sanity check on any off-pool or live-drifted
contract (a live delta drifting out of band still means the position no longer
resembles the studied cohort).
