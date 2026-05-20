# AI Coding Guardrails for Algo Trading Development

**Source**: `algo_trading_implementation_library/09_agentic_coding_workflows/{anti_bloat_rules, project_rules, codex_guardrails}`

> Anti-bloat rules, project hard rules, and Codex/Cursor/Windsurf guardrails for AI-assisted quant development.

---

## Key Concepts

### Anti-Bloat Discipline
- **File creation rule**: Only create a new file if it represents a new module boundary, prevents mixed-purpose files, or is a required output artifact.
- **Named file anti-patterns**: Never create `*_new.py`, `*_final.py`, `*_working.py`, `*_fixed.py`, or `*_temp.py`. These indicate iterative flailing, not intentional design.
- **Refactor-in-debug rule**: No broad refactoring while debugging. Isolate the failing invariant first.

### Project Hard Rules (10 Commandments)
1. No new files unless the change requires it.
2. No refactoring of protected paths without explicit instruction.
3. No silent changes to strategy assumptions.
4. No silent changes to data windows.
5. No silent changes to transaction costs.
6. No modifying test windows after seeing results (prevents p-hacking).
7. Every backtest run must produce a [[run manifest]].
8. Every metric formula must be centralized (no scattered formulas).
9. Every strategy must use the same module contract.
10. Every bug fix must include a regression test.

### Protected Paths (Never Touch Without Explicit OK)
- `src/core/contracts.py` — interface definitions for the entire system
- `src/core/ledger.py` — accounting/tracking backbone
- `src/core/risk.py` — risk constraint enforcement
- `src/core/metrics.py` — centralized performance calculations
- `configs/` — reproducible experiment configuration
- `data_versions/` — data lineage tracking
- `reports/` — immutable output artifacts

### Codex/Cursor/Windsurf Prompt Guards
- **Never** ask the agent to "make it profitable" — this causes the AI to silently alter assumptions to produce desired results.
- **Do** ask for specific implementations: tests, metrics, diagnostics.
- **Anti-bloat command**: Force the agent to list files it will modify before writing code.
- **Bad prompt**: "Improve the strategy and find better parameters." → opens the door to result-contamination.
- **Good prompt**: "Implement `max_drawdown` and `time_under_water` in `src/core/metrics.py`. Add unit tests. Do not modify strategy code." → surgical, verifiable.

---

## Implications for Trading Systems

- **Reproducibility**: Protected paths + centralized metrics guarantee that two runs with the same inputs always produce the same outputs — essential for comparing strategies fairly.
- **Audit trail**: The 10 hard rules create a paper trail for every decision, making it possible to answer "why does this strategy perform like this?" months later.
- **AI safety**: Codex guardrails prevent the worst failure mode of AI coding: silent assumption changes that inflate backtest results.
- **Team safety**: Even in solo development, treating the AI as a junior dev who needs explicit guardrails prevents "helpful" changes that corrupt experiments.

---

## Failure Modes

| Failure | Consequence | Guard |
|---|---|---|
| AI silently changes cost model | Backtest becomes optimistic fake | Rule 5: no silent cost changes |
| AI creates `strategy_final_v2.py` | File proliferation, confusion | Anti-bloat named file blacklist |
| AI refactors `core/metrics.py` while debugging strategy | Breaks all other strategies' metric calculations | Protected paths rule |
| User asks AI to "make it profitable" | AI overfits to desired result, destroys edge | Codex guardrail: never ask this |
| Bug fix without regression test | Same bug re-introduced in next iteration | Rule 10: regression test mandatory |
| New test window after seeing bad results | P-hacking / data snooping bias | Rule 6: immutable test windows |

---

## Cross-Links

- [[strategy-backtest-contracts]] — the contracts that guarded paths enforce
- [[Agentic Workflow Patterns]] — how to structure AI coding sessions
- [[strategy-templates-standards]] — the templates these rules protect
- [[Data Quality Checks]] — how data versioning integrates with protected paths
- [[Schema Catalog]] — the schemas that define artifact outputs
