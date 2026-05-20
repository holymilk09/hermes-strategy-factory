# Walk-Forward Epoch Protocol

The 8-step protocol for running a single walk-forward evaluation epoch of a trading strategy.

## Protocol

1. **Define hypothesis and falsification rule** — What are you testing and what would disprove it?
2. **Lock train/validation/test dates** — No peeking. Dates are fixed before training.
3. **Train or select parameters** — Only on train/validation data.
4. **Evaluate once on test** — One shot. No second chances on the same test set.
5. **Run stress and cost sensitivity** — 2x/3x costs, parameter neighborhood analysis.
6. **Generate heatmaps** — Parameter heatmaps and regime-segmentation heatmaps.
7. **Write review** — What changed, what improved, what degraded, what's the next test.
8. **Decide: promote, reject, or hold** — Promote only if it passes all gates (DSR, PBO, regime tests).

## Example Walk-Forward Schedule

| Epoch | Train | Validation | Test | Decision |
|---|---|---|---|---|
| E001 | 2018-2021 | 2022 | 2023 | hold — underperforms high-vol chop; add regime gate |
| E002 | 2019-2022 | 2023 | 2024 | reject — too similar to E001 after cost adjustment |
| E003 | 2020-2023 | 2024 | 2025 | promote to paper — regime gate added, OOS Sharpe stable |

## Golden Rules

- **Never move test windows after seeing bad results.**
- **Never reuse test set until it passes.**
- **One evaluation per test set.** If you retrain and retest on the same test, it's no longer OOS.
- **Promotion requires multiple gates pass:** DSR-adjusted Sharpe, PBO < 30%, acceptable weak-point score, cost-sensitivity robustness.

## Implications

- The epoch protocol prevents the most common backtesting failure: iterating until the result looks good.
- Holding a strategy (neither promoting nor rejecting) is a valid decision that buys time for the next epoch.
- Heatmaps reveal whether the strategy works broadly or only at one lucky parameter setting.

## Failure Modes

- **Sliding the OOS window** after poor results destroys the test's validity.
- **Parameter over-selection**: choosing the "best" parameter from a heatmap without considering stability across neighbors.
- **Promoting on a single metric**: e.g., good Sharpe but drawdown exceeds the acceptable threshold.
- **Epoch too short/long**: too short = not enough market states; too long = slow to detect degradation.

## Cross-Links

- [[Epoch-Learning-Retraining]] — the epoch model this protocol operationalizes
- [[Trading-System-Build-Doctrine]] — Phase 3 backtesting and validation
- [[Strategy-Weak-Point-Detection]] — heatmaps feed weak-point diagnosis
- [[Papers-Docs-Synthesis#strategy-development-process]] — Peterson's experiment design framework
