Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: ENTRY-side, not exit. Entry-day tradeability graded from the 09:52 ET liquidity snapshot; outcome measured as end-of-day contract volume. N=750 over 15 entry days.
Source: the GammaRips engine 15-day study (pool_liquidity_snapshot), relayed 2026-07-28 evening — docs/ENGINE-RESPONSE-TRADEABILITY-2026-07-28.txt; harness discovery + single-session measurement in docs/POOL-LIQUIDITY-FINDING-2026-07-28.txt
Date: 2026-07-28

# Early prints predict tradeability; nothing else does

**~43% of the curated pool's recommended contracts are effectively untradeable on entry
day** (pooled 42.8% under 50 contracts across 15 days; daily median 42%, range 28–70%;
22.3% are ghosts under 10 contracts). This is structural and daily, not a bad session.

## The rule

`day_volume` in the recommended contract at the **09:52 ET** snapshot:

| Prints by 09:52 | Finished day ≥50 contracts |
|---|---|
| ≥ 20 | 100% (N=133) |
| ≥ 5 | 96.3% (N=218) |
| ≥ 1 | 84.5% |
| 0 | 31.9% (40.6% ghost, 68.1% under-50) |

Zero prints at 09:52 is **veto-grade caution** — it makes doctrine hard-exclusion #3
("unverifiable liquidity you are not willing to own") objective for the first time. It is
a strong prior, not an automatic kill: 32% of zero-print names still recover.

**Timing floor:** the feed is 15-minute delayed. A 09:42 read shows nothing real; 09:52
is the first usable snapshot. Reading earlier and calling it decision-time state is a
self-inflicted outage. Also read `day_last_updated` — ~24% of early-session rows carry a
prior-day bar and must be graded as "0 traded so far today," never as a live mark.

## Precedence

**prints > THIN flag > OI level (tiebreak only).**

- THIN (`expected_liquidity`, engine-side): underlying share volume ≤2.5M AND active
  strikes ≤15 AND contract OI ≤1000. Precision ~0.60 at flagging ghosts. Not yet exposed
  through the MCP — a logged product gap.
- OI ≥1000 still leaves **23.9%** of contracts under-50 on entry day. See
  [[oi-not-quality-signal]] for the amended reading: OI carries genuine rank signal for
  tradeability (Spearman +0.48) but is useless as a threshold gate.

## Root cause (engine-confirmed, with one correction)

The enrichment gate qualified the **name** on aggregate directional UOA, then a
delta-targeting step chose a **contract** with no liquidity test of its own. Name-level
flow laundered ghost strikes: UNP carried $5.19M of call flow into a strike that traded 6
contracts, while PGY carried $1.29M into one that traded 2,123. The harness originally
proposed "never use OI"; the engine corrected this to **saturation** — the picker's OI
score maxed out at OI=200, so 87% of the pool scored perfectly liquid and 16% of those
were ghosts. Fixes deployed 2026-07-28, first live pool 2026-07-29 (OI scale extended
log-style to ~3000, sweep-volume influence halved, thin-name demotion). Replay estimate:
ghost rate 22.3% → 12.1%, under-50 42.8% → 31.5%.

## Why it matters

Thin and wide are **different things** and must not be conflated. The 2026-07-28 UNP
entry had 4 prints by 10:00 and 7 contracts all session. With the
underlying down 0.49%, the position quoted down 35%: roughly 9% delta, 4% IV/theta, and
~22% quote width. Later fills at 2.50/2.40 showed the spread had tightened to ~4% by
afternoon, so width varies intraday while volume does not lie. Same day, same pool, GM
traded 296 contracts and round-tripped on demand at +25.9%. The difference between the
two trades was not thesis quality.

## Downstream consequence

When consulting `query_outcomes` history per ticker, **filter or discount
`illiquid_exit=true` rows** — only 37% of ghosts were caught by `INVALID_LIQUIDITY`, and
79% carry `illiquid_exit`. Unfiltered, ghost rows show near-zero sim returns no human
could realize, biasing any per-name conclusion.

Related: [[oi-not-quality-signal]], [[voi-ratio-anti-edge]], [[entry-1000-et]].
