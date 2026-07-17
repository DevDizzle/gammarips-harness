---
name: exit-plan
description: Design the exit for the selected contract BEFORE entry, from the opportunity surface and outcome history. Runs after /select-contract; output is the journal's Exit plan section.
---

# exit-plan

The exit is where the PnL lives ([[fixed-exit-composites-negative]]): the pool's
opportunity is real (median peak +21%, p90 +123%) but every uniform fixed exit tested is
negative. So the exit is designed per-trade, before entry, from evidence.

## Procedure
1. **Choose the intended hold first** (same-day vs multi-day). This determines which wiki
   levers are even admissible (exit-context discipline) and what the time-stop is.
2. **Pull the evidence:**
   - `query_outcomes(view="surface")` — MFE/MAE distribution for comparable pool contracts
     (filter toward the candidate's delta bucket / score via `query_outcomes(view="labels")`
     + `query_outcomes(view="summary", group_by='delta_bucket')`).
   - `query_outcomes(view="exit_rule", target_pct=, stop_pct=, horizon=)` for 2–3 candidate
     brackets — compare est_win_rate and EV bounds; note the `heuristic_share` honestly.
3. **Design:** target, stop, and a **mandatory time-stop** (doctrine). State WHY these
   levels for THIS contract — e.g. "stop below the median trough −30% is noise-harvesting;
   MAE distribution says −25 stops out half the eventual winners."
4. **Pre-commit the management rule:** what, if anything, may be adjusted intraday
   (risk-reducing direction only, per doctrine).
5. **Output:** the journal `## Exit plan` block, including the tool evidence in one or two
   lines each.

**Boundary:** these tools surface evidence; they never gate. If they can't discriminate
between your brackets — or can't score your exit style at all (trailing, discretionary) —
say so, write the uncertainty into the journal, and proceed on judgment. Never downgrade to
no-trade for lack of exit-validation data; only the doctrine hard exclusions veto.
