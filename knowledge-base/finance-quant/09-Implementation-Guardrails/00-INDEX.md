# Implementation Guardrails — Index

Agentic AI coding guardrails, contracts, workflow patterns, and template standards for building and maintaining algorithmic trading systems.

**Source**: `algo_trading_implementation_library/09_agentic_coding_workflows/` and `10_templates/`

---

## Notes

### [[AI Coding Guardrails]]
Anti-bloat rules, project hard rules, protected paths, and Codex/Cursor/Windsurf prompt guards. Prevents AI-assisted development from silently corrupting experiments.

### [[strategy-backtest-contracts]]
Mandatory interfaces: 12 required strategy fields, 3 required methods, backtest input/output checklists, and the reproducibility invariant (same inputs → same outputs).

### [[Agentic Workflow Patterns]]
Standardized 6-step task sequence, 10-step strategy implementation sequence, and 4 prompt templates (paper→hypothesis, implement strategy, debug discrepancy, weak-point review).

### [[strategy-templates-standards]]
Concrete templates: strategy README (14 sections), research-to-hypothesis mapping, review report with Promote/Reject/Hold decision, run manifest JSON schema, and standard project tree.

---

## Quick Reference

| Want to... | Go to |
|---|---|
| Set up AI coding session rules | [[AI Coding Guardrails]] |
| Define strategy interface | [[strategy-backtest-contracts]] — Strategy Contract |
| Define backtest requirements | [[strategy-backtest-contracts]] — Backtest Contract |
| Run an AI coding session | [[Agentic Workflow Patterns]] — Standard Task Sequence |
| Implement a new strategy | [[Agentic Workflow Patterns]] — Implementation Sequence |
| Convert research to strategy | [[strategy-templates-standards]] — Hypothesis Template |
| Document a strategy | [[strategy-templates-standards]] — README Template |
| Review a backtest run | [[strategy-templates-standards]] — Review Report Template |
| Set up a project | [[strategy-templates-standards]] — Project Tree |
| Track a backtest run | [[strategy-templates-standards]] — Run Manifest |
| Review data contracts and Python code patterns | [[Code Templates and Schemas]] — contracts.py, sample strategy, YAML configs, JSON schemas, test fixtures |
