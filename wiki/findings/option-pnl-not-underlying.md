Status: active
Type: finding
Tag: proven-on-cohort
Exit-context: n/a (methodology)
Source: the GammaRips engine UNDERLYING_VS_OPTIONS_V1; memory reference_option_pnl_research_label
Date: 2026-07-06

# Evaluate on option PnL, never underlying direction

On the same pool, **underlying-up hit 54% while option-up hit only 41%** — theta, IV, and
spread eat a directional win. Any rule, edge, or track-record claim evaluated on
underlying direction overstates reality.

Application: every journal outcome and every wiki finding is stated in option PnL. MCP
caveat: `get_signal_performance` / `get_win_rate_summary` report **underlying-direction**
outcomes (they carry a universe marker) — never quote them as option performance. Option
PnL lives in `query_outcomes` / `get_outcome_summary` / `get_opportunity_surface`.
