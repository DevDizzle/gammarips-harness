# eval/ — the harness's own labeled dataset

This directory replaced the journal (retired in the trade/review consolidation): instead
of one narrative note per day, the harness pre-registers **one structured row per pool
name per day** — including every name it screened out — and scores all of them after the
close. That is what lets `scripts/edge.py` and `scripts/skill_eval.py` say whether the
screen beats the pool it draws from, instead of a diary saying it felt good.

The data files below are YOURS — they start empty and accumulate as you run the loop.
Commit them to your fork if you want the track record in git (recommended: append-only
history is what makes it honest), or gitignore them if you prefer.

| File | Written by | What |
|---|---|---|
| `funnel-log.jsonl` | `/trade` (pre-registration) + `/review` (outcomes) | one row per pool name per decision day |
| `trades.jsonl` | you, via the session, on a real fill | actual fills only — never the plan |
| `behavior-ledger.jsonl` | `/coach` | behavioral events (leaks, wins, observations) with evidence |
| `FINDINGS.md` | `/review`, rarely | accumulated evidence, each entry with its N |

`scripts/funnel_log.py` and `scripts/behavior_log.py` validate on every write. Run their
`check` after any manual edit.

## Funnel row schema

Stages: `pool` → `shortlist` → `candidate` → `entered`. Exclusion reasons:
`delta_band`, `moneyness_below`, `moneyness_above`, `live_drift`, `liquidity`,
`earnings`, `head_to_head`, `operator_declined`, `timing`, `regime`, `none` (entered
rows only). The `scan` block carries the point-in-time features so outcomes can be
joined against what was known at decision time. `skill_version` stamps which version of
`/trade` produced the row — without it, rows from before and after a skill change are
not comparable.

Synthetic example (invented ticker, invented numbers — the shape, not a trade):

```json
{"entry_day":"2026-01-15","scan_date":"2026-01-14","ticker":"EXMPL",
 "contract":"O:EXMPL260220C00050000","funnel_stage":"candidate",
 "exclusion_reason":"operator_declined",
 "note":"RANKED #2. 14 prints by 09:52 (liquidity-confirmed), OI build +240, live delta 0.33.",
 "scan":{"delta":0.34,"moneyness_pct":0.11,"overnight_score":6,"mom_60":0.21,"mid":1.20,
         "atr_norm_move":0.9,"catalyst_score":0.65},
 "skill_version":"v1","regime":{"vix":14.2,"vix3m":16.1,"spy_trend":"BULLISH","rail":"PASS",
 "as_of":"2026-01-14","note":"labeled substrate lags live pool 1-2 sessions"},
 "outcome_session":null,"outcome_3d":null}
```

`/review` later fills `outcome_session` (10:00 ET anchor, post-anchor MFE/MAE/close,
touch flags) and `outcome_3d` (the 3-session window — where most winners actually peak).
Rows that never printed get `unlabeled_illiquid`, not fake scores.

## FINDINGS.md discipline

Append only when the accumulated evidence moves or a process failure cost a real
decision. Every claim carries its N, its cohort, and its exit context. Most days add
nothing — that is the correct output.
