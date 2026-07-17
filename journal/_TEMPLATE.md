# YYYY-MM-DD — TICKER (or NO-TRADE)

Status: draft
Committed-at: (ET timestamp, set only when trade-critic passes)

## Pool context (point-in-time)
scan_date, entry day, pool size, regime (vix_at_scan / vix3m / rail pass), anything
excluded and why.

## Candidate
Contract (ticker, strike, expiry, type), key features at scan time (delta, moneyness,
overnight_score, mom_60 if exposed), why it beat the shortlist.

## Thesis
2–5 sentences. Every claim cites a wiki note as `[[note-slug]]` with its tag stated, and
notes whether the note's Exit-context matches the planned hold.

## Liquidity check
What the MCP could and could not verify (session-frozen caveat). Accept-and-document or
pass rationale.

## Exit plan (designed BEFORE entry)
Target / stop / mandatory time-stop, intended hold, and the opportunity-surface evidence
consulted (`query_outcomes(view="surface")`, `query_outcomes(view="exit_rule")` results in
brief).

## Sizing
Paper notional (set your own — record the chosen size AND its rationale). Real-money
arithmetic practiced: "on a $X account this risks Y%."

## Critic
trade-critic verdict + objections raised and how each was resolved.

---
(Everything above is immutable once Status: committed. Everything below is appended later.)

## Outcome
Entry (time, mark, source), exit (time, price, reason: target/stop/time-stop/discretion),
option PnL %, MFE/MAE if known. For no-trade days: what happened to the shortlist anyway,
if checked.

## Lessons
Wiki-distill candidates? One honest sentence on process quality separate from outcome
quality.
