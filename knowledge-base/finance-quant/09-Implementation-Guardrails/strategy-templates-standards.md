# Strategy Templates and Review Standards

**Source**: `algo_trading_implementation_library/10_templates/{README_strategy_template, review_report_template, project_tree, research_to_strategy_hypothesis_template, run_manifest_template, sample_strategy, src/contracts}`

> Concrete template patterns for strategy documentation, review reports, project structure, and the research-to-strategy pipeline.

---

## Key Concepts

### Strategy README Template — 14 Sections

Every strategy gets a README with these sections:

| Section | Purpose |
|---|---|
| **Strategy ID** | Unique identifier |
| **Hypothesis** | The edge — what, why, when |
| **Universe** | Tradable Instruments |
| **Horizon** | Holding period in bars/time |
| **Signal** | How signals are generated |
| **Entry** | Position open logic |
| **Exit** | Position close logic |
| **Sizing** | Position size determination |
| **Risk Controls** | Limits and constraints |
| **Data Required** | Input data specification |
| **Cost Model** | Commission + slippage |
| **Falsification Criteria** | Rejection conditions (defined upfront) |
| **Known Failure Modes** | Where this strategy is known to break |
| **Current Status** | Research → Backtest → Paper → Live → Retired |

### Research-to-Strategy Hypothesis Template

Maps academic/paper research to testable hypotheses:

- Source → Claim from source → Tradable hypothesis → Data needed → Observable timestamp rule → Signal formula → Entry/exit rules → Risk assumptions → Cost assumptions → Falsification test → Implementation notes

This template forces the research-to-implementation bridge to be explicit, preventing invented performance claims.

### Review Report Template — Decision Framework

After a backtest run, produce a review with:

1. **Run identity** — links to run manifest
2. **Summary** — what happened in plain language
3. **What changed** — diff from last run
4. **Metrics** — numbers from metric pack
5. **Heatmap findings** — parameter sensitivity
6. **Weak points** — top vulnerabilities
7. **Data issues** — gaps, survivorship, look-ahead
8. **Execution issues** — slippage, fill, liquidity
9. **Overfit risk** — parameter stability assessment
10. **Decision** — Promote / Reject / Hold
11. **Next experiment** — single recommended falsification test

### Run Manifest — Immutable Run Record

JSON structure capturing: `run_id` (timestamp + strategy + code hash), `strategy_id`, `code_version` (git commit), `config_hash`, `data_version`, `feature_version`, `model_version`, date range, universe, cost/slippage models, random seed, environment, and output file paths for equity curve, trade ledger, metric pack, review report.

### Project Tree Template

Standard structure separating concerns:

```
trading_bot/
  README.md, pyproject.toml
  configs/        (strategy.yaml, risk_limits.yaml)
  data/           (raw/, normalized/, features/, quality_reports/)
  src/core/       (contracts, data, features, strategy, portfolio, risk, execution, broker, ledger, metrics, review)
  src/strategies/ (one file per strategy)
  src/tools/      (run_backtest, make_report, make_heatmaps)
  tests/          (fixtures, test_features, test_signal, test_risk, test_ledger, test_metrics)
  reports/        (runs/, reviews/)
```

---

## Implications for Trading Systems

- **Self-documenting codebase**: The README + hypothesis template mean any strategy can be understood without reading implementation code.
- **Lifecycle tracking**: The 5-stage status field (Research → Backtest → Paper → Live → Retired) provides portfolio-level visibility into strategy maturity.
- **Decision discipline**: The Promote/Reject/Hold review decision forces closure — strategies don't linger in undefined states.
- **Immutable history**: Run manifests with git commit + config + data hashes mean every result can be fully reconstructed.
- **Concern separation**: The project tree physically enforces that strategy logic, core infrastructure, and test code never mix.
- **Falsification culture**: Every template includes explicit rejection criteria, fighting the natural tendency to "keep tweaking until it looks good."

---

## Failure Modes

| Failure | Consequence | Prevention |
|---|---|---|
| Strategy README missing falsification criteria | No objective stopping point | 14-section template validation |
| Review with no decision | Strategy limbo, wasted compute | Decision field mandatory |
| Run manifest missing data version | Can't reproduce results | Hash-based manifest schema |
| Core logic mixed into strategies directory | Harder to isolate bugs, shared bugs spread | Project tree structure enforces separation |
| Review recommends multiple "next steps" | Undisciplined experiment proliferation | Single falsification test only |
| Falsification test invented after seeing results | Confirmation bias | Pre-define in hypothesis template |
| No config hash in manifest | Can't determine what changed between runs | Config hash required field |

---

## Cross-Links

- [[AI Coding Guardrails]] — rules that protect these templates from silent modification
- [[strategy-backtest-contracts]] — the formal interface these templates implement
- [[Agentic Workflow Patterns]] — how to produce these templates using AI workflows
- [[Run Manifest Structure]] — detailed field definitions
- [[Schema Catalog]] — JSON schemas for the artifact outputs
- [[Data Quality Checks]] — the data quality section of the review report
