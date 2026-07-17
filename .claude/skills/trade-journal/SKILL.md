---
name: trade-journal
description: Create, commit, or close a journal entry. Enforces point-in-time discipline and the trade-critic gate. Use to record today's decision (trade or no-trade) and later to record outcomes.
---

# trade-journal

The journal is the harness's dataset — its integrity is what makes the paper track record
count toward the real-money triggers. Rules live in `docs/TRADING-DOCTRINE.md` and this
repo's README.

## Create + commit (decision time)
1. Copy `journal/_TEMPLATE.md` → `journal/YYYY-MM-DD.md` (today, ET). One file per day,
   no-trade days included.
2. Fill every pre-commit section from the `/morning-pool`, `/select-contract`,
   `/exit-plan` outputs. Outcome/Lessons stay empty.
3. **Run the trade-critic subagent** on the draft. FAIL → resolve each objection (or
   downgrade to no-trade) and re-run. PASS → record the verdict in `## Critic`, set
   `Status: committed` (or `no-trade`) + `Committed-at` (ET).
4. `python scripts/lint.py` — must pass.
5. When the position is (paper-)entered, set `Status: open`.

## Close (outcome time)
1. Append `## Outcome` — entry/exit/PnL%/exit reason. **Never edit pre-commit sections.**
2. Fill `## Lessons`: one sentence on process quality *separate from* outcome quality
   (good process + bad outcome is fine; the reverse is the dangerous one).
3. Propose wiki-distill candidates (recurring lesson → `/wiki-distill`).
4. Set `Status: closed`; run `python scripts/lint.py`.
