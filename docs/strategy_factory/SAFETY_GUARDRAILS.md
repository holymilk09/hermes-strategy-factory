# Strategy Factory — Safety Guardrails

Updated: 2026-05-27

---

## Model Guardrails

| Rule | Enforcement |
|---|---|
| Strategy engine frozen during maturity | Manual — healthcheck includes invariants |
| No threshold changes without new maturity process | Policy — documented in runbook |
| No scoring changes without new maturity process | Policy — documented in runbook |
| No new timeframe without separate horizon_id and maturity tracking | Design constraint — not yet implemented |
| No premarket/after-hours in official maturity | Design constraint — OHLCV data is daily only |
| No options in MVP | Product scope constraint |
| No broker/live/shadow | Hard block in healthcheck, watchdog, and all scripts |

## Data Guardrails

| Rule | Enforcement |
|---|---|
| Maturity counts OHLCV bars after signal timestamp, not calendar days | Code — `timestamps[timestamps > signal_ts]` |
| Missing bars do not count toward maturity | Implicit — no row in CSV means no timestamp to compare |
| Holidays/weekends excluded because no OHLCV row exists | Implicit — yfinance returns no bar |
| No fabricated outcomes | All outcomes from real OHLCV closing prices |
| yfinance production claims require terms review | Policy — not yet reviewed |
| Raw real-time data redistribution requires vendor/license review | Policy — not yet addressed |

## Product Guardrails

| Rule | Enforcement |
|---|---|
| $5 tier is one-to-many Edge Sheet only | Design constraint |
| No personalized recommendations | Product scope + wording layer |
| No "buy/sell now" wording | Banned words list in `retail_wording.py` |
| No custom portfolio advice | Product scope |
| No performance claims until enough tracked outcomes exist | Policy — no trust state without completed outcomes |
| No win-rate claims without sample size and methodology | Policy — scoreboard shows raw data, not derived metrics |
| No "AI predicts winners" marketing | Product scope — no ML in MVP |
| All outputs carry research-only disclaimer | Code — `DISCLAIMER` constant in `retail_wording.py` |

## Engineering Guardrails

| Rule | Enforcement |
|---|---|
| Branch before feature work | Policy |
| Narrow explicit-path staging only | Policy — documented in REPO_ORGANIZATION_POLICY.md |
| No broad `git add .` or `git add -A` | Policy |
| No `git clean` unless explicitly approved | Policy |
| No `git reset --hard` | Policy |
| No moving files until audit identifies canonical owners | This document serves as that audit |
| Generated reports are runtime artifacts, not source | Policy — REPO_ORGANIZATION_POLICY.md |
| Runtime artifacts stay uncommitted | Policy |
| Local configs stay untracked | .gitignore pattern (if applicable) |
| `reports/edge_sheet/` and `reports/strategy_factory/` are generated — never edited by hand | Policy |

## Missing Risks Checklist

| Risk | Coverage | Recommended Action |
|---|---|---|
| Small sample false confidence | COVERED | HEALTHCHECK_PASS_CONTINUE_WAITING until outcomes resolve |
| Baseline-relative comparison | PARTIAL | Scoreboard compares to signal price. Consider benchmark-relative metric. |
| Good strategy during bad market | PARTIAL | Market Weather gate exists but not yet cross-validated |
| Over-filtering | COVERED | Ghost ledger tracks rejected symbols |
| Ghost tracking | COVERED | Ghost ledger in production |
| Survivorship bias | PARTIAL | Ghost ledger partially covers this. Need explicit detection of symbols that disappeared from universe. |
| Lookahead leakage | COVERED | `timestamps > signal_ts` guard in observation code |
| Corporate actions / splits / dividends | ABSENT | yfinance auto_adjust=True handles splits/dividends. Need explicit verification and documentation. |
| Sector clustering | PARTIAL | Universe includes multiple sectors. No sector concentration gate yet. |
| Popular ticker bias | PARTIAL | Documentation needed in Edge Sheet that coverage is tilted toward liquid names |
| Timeframe confusion | PARTIAL | MVP is swing-only. Per-horizon tracking needed if adding more timeframes. |
| "No Edge" can still go up | COVERED | Retail wording drops "No Edge" when price moves — scoreboard tracks this |
| "Setup Breaks Below" mistaken for stop-loss advice | PARTIAL | Need explicit retail wording that this is a research observation, not a trading recommendation |
| Watchlist personalization advice risk | DEFERRED | Not relevant until Watchlist Lite phase |
| Marketing performance claim risk | COVERED | Compliance language on every output |
| Email/SMS compliance | DEFERRED | Not relevant until notification features |
| Data redistribution rights | PARTIAL | yfinance TOS not reviewed for commercial redistribution |
| Branch/dirty-tree management | PARTIAL | REPO_ORGANIZATION_POLICY.md exists. Need automated dirty-tree detection in healthcheck. |
| Report verbosity | COVERED | Compact format standard adopted |
| ML premature deployment | COVERED | ML phases gated behind completed outcomes |
| AI assistant hallucination risk | COVERED | No AI assistant in MVP |
| Customer support burden | DEFERRED | Not relevant until paid tier. Need support scope doc. |

## Future Guardrails (not yet implemented)

- `future_bars` must never decrease unless data repair mode is active (monotonic assertion)
- Add dividend/split adjustment audit to healthcheck
- Add sector concentration report to scoreboard
- Add stale ticker detection (symbols that dropped from universe)
- Add dirty-tree detection to healthcheck
- Add benchmark-relative return to scoreboard rows