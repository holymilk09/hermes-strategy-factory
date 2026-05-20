# Agentic Workflow Patterns

**Source**: `algo_trading_implementation_library/09_agentic_coding_workflows/{workflow, prompts}`

> Standardized AI coding session workflows, prompt patterns, and the 10-step strategy implementation sequence.

---

## Key Concepts

### Standard AI Task Sequence (6 Steps)

1. **Read context**: `README.md`, `project_rules.md`, and relevant contract files.
2. **Declare changes**: State intended file modifications before writing.
3. **Minimize scope**: Modify the smallest possible surface area.
4. **Run tests**: Execute test suite.
5. **Produce diff summary**: Document what changed and why.
6. **Update docs**: Update run/review documentation if strategy logic changed.

### Strategy Implementation Sequence (10 Steps)

1. Add hypothesis file → Define the edge
2. Add feature function → Data transformation
3. Add signal function → Trading logic
4. Add sizing config → Position management
5. Add risk rule if needed → Constraint enforcement
6. Add tests → Verify correctness
7. Add backtest config → Experiment setup
8. Run baseline → Generate initial results
9. Generate report → Artifact creation
10. Write review → Decision documentation

### Prompt Patterns

#### Convert Paper to Hypothesis
> Extract only testable trading hypotheses from the paper. Output JSON with: asset_class, universe, horizon, signal, regime_filter, entry_rule, exit_rule, cost_model, falsification_test, required_data, implementation_difficulty. Do not invent performance claims.

#### Implement Strategy Module
> Implement the strategy described in `strategy_contract.md`. Only modify `src/strategies/<strategy_id>.py` and `tests/test_<strategy_id>.py`. Do not modify data pipeline, metrics, or execution code. Use existing contracts.

#### Debug Backtest Discrepancy
> Compare expected ledger vs actual ledger for `run_id=<id>`. Trace data → signal → target → order → fill → cash → position → metric. Return the first divergent event and likely cause.

#### Weak-Point Review
> Given `metric_pack.json`, `trade_ledger.csv`, `parameter_grid.csv`, and `regime_report.csv`, identify the top 5 weak points. Classify each as strategy, data, execution, risk, code, or overfit. Recommend the next falsification test only.

### Principles Behind the Patterns

- **Narrow scope**: Every prompt targets a specific output, not a vague goal.
- **Boundary discipline**: Prompts explicitly state what NOT to touch.
- **Evidence-based debugging**: Trace through the ledger chain at every divergence point.
- **Single recommendation**: At review, recommend only the next falsification test — not a list of "things to try."

---

## Implications for Trading Systems

- **Reproducible sessions**: The 6-step sequence creates a standardized interaction pattern that can be audited and repeated.
- **Reduced scope creep**: Declaring changes before writing prevents accidental modification of protected systems.
- **Ledger-chain debugging**: Tracing through the full event chain (data → signal → target → order → fill → cash → position → metric) is the most reliable way to find where a backtest went wrong.
- **Research-to-implementation pipeline**: The paper-to-hypothesis prompt bridges academic research to testable code without inventing claims.

---

## Failure Modes

| Failure | Consequence | Prevention |
|---|---|---|
| AI modifies multiple files beyond scope | Breaks unrelated systems | Step 2: declare changes; good prompts specify file boundaries |
| Skipping tests | Undetected bugs in signal logic | Step 4: run tests mandatory |
| Vague prompts like "make it better" | Unpredictable, often harmful changes | Use template prompts, not goal-seeking language |
| No review after baseline run | Over-optimistic deployment | Steps 9-10: report + review mandatory |
| Debugging without ledger trace | Guessing at root cause | Use the ledger-chain debug prompt |
| Multi-action review recommendations | Undisciplined experimentation | "Recommend the next falsification test only" |
| Not updating docs after strategy change | Lost institutional knowledge | Step 6: update run/review docs |

---

## Cross-Links

- [[AI Coding Guardrails]] — the rules that these workflows operate within
- [[strategy-backtest-contracts]] — the contracts that define the interfaces in the prompt templates
- [[strategy-templates-standards]] — the concrete artifacts produced by steps 9-10
- [[Data Quality Checks]] — where the ledger trace may diverge
- [[Feature Store Design]] — feature functions in step 2 of the implementation sequence
