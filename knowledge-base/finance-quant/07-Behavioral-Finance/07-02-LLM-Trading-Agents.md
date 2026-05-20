# LLM Trading Agents & Multi-Agent Orchestration

> **Group F** — Synthesized from raw research library
> **Tags:** LLM-trading, multi-agent, GPT-Signal, TradingAgents, FinMem, QuantAgent, behavioral-consistency, agent-simulation
> **Cross-links:** [[07-01-Behavioral-Finance]], [[07-Index]]

## Key Papers

### Tier 1 — Core LLM Trading Research

- **Kou et al. (2024)** — *Automate Strategy Finding with LLM in Quant Investment* (arXiv:2409.06289, FREE). Uses LLMs to automate parts of the quantitative strategy discovery pipeline. Must be paired with backtest-overfitting research before trusting any generated strategy.
- **Wang et al. (2024)** — *GPT-Signal: Generative AI for Semi-Automatic Feature Engineering in the Alpha Research Process* (arXiv:2410.18448, FREE). LLMs for feature ideation rather than autonomous trading. Closer to a credible alpha-research workflow. The paper demonstrates that LLMs may be better at generating hypotheses than executing them.
- **Xiao et al. (2024)** — *TradingAgents: Multi-Agents LLM Financial Trading Framework* (arXiv:2412.20138, FREE). Representative multi-agent LLM trading framework with role-separated agents (researcher, analyst, trader, critic). Useful as architecture reference, not as proof of profitable execution.
- **Lopez-Lira (2025)** — *Can Large Language Models Trade?* (arXiv:2504.10789, FREE). Direct empirical test of whether LLMs can generate trading-relevant signals. The critical checkpoint paper: use its findings as an empirical baseline before building agentic systems around LLM reasoning.
- **Henning et al. (2025)** — *LLM Trading: Analysis of LLM Agent Behavior in Experimental Asset Markets* (arXiv:2502.15800, FREE). Studies LLM agents as market participants in experimental settings. Evaluates whether LLM decision behavior is stable under trading incentives — a key validity question.
- **Li et al. (2026)** — *Behavioral Consistency Validation for LLM Agents* (arXiv:2602.07023, FREE). Proposes methods to validate behavioral consistency in LLM agents. Critical insight: a trading agent that changes its behavior under prompt perturbation is not a strategy, it is a liability.

### Tier 2 — Architecture and Simulation

- **Yu et al. (2023)** — *FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design* (arXiv:2311.13743, FREE). Memory-augmented LLM trader with layered retrieval. Good reference for comparing dynamic memory against deterministic feature stores.
- **Park et al. (2023)** — *Generative Agents: Interactive Simulacra of Human Behavior* (UIST / arXiv:2304.03442, FREE). The ancestor of all agent-based simulation including financial agents. Introduces memory-reflection-planning architecture. Useful for architecture design, not financial validity.
- **Li, Yu, Haohang et al. (2023)** — *TradingGPT: Multi-Agent System with Layered Memory and Distinct Characters for Enhanced Financial Trading Performance* (arXiv:2309.03736, FREE). Early LLM trading-agent architecture with memory and role separation. Useful baseline for what agent frameworks typically overclaim.
- **Quan/Ding et al. (2024)** — *Large Language Model Agent in Financial Trading: A Survey* (arXiv:2408.06361, FREE). Comprehensive map of LLM trading-agent literature. Read after primary papers to avoid absorbing survey framing uncritically.
- **Vidler & Walsh (2024)** — *TraderTalk: Analyzing Large Language Model Behavior in Simulated Financial Markets* (arXiv:2410.21280, FREE). Studies LLM strategic communication behavior in simulated markets. Tests whether agent conversations add signal or only generate narrative.
- **Hashimoto et al. (2025)** — *Agent-Based Simulation of a Financial Market with LLM-Based Agents* (arXiv:2510.12189, FREE). Financial market simulation populated by LLM agents. Separates agent believability from actual alpha generation.
- **del Rio-Chanona, Pangallo & Hommes (2025)** — *Can Generative AI Agents Behave Like Humans?* (arXiv:2505.07457, FREE). Evaluates generative AI agents on generic human decision-making tasks. Tests whether LLM agents are valid behavioral stand-ins for market simulation.
- **Wang/Xiong et al. (2025)** — *QuantAgent: Seeking Holy Grail in Trading by Self-Improving LLM* (arXiv:2509.09995, FREE). Self-improving LLM agent for quantitative trading. Requires skepticism: self-improvement can easily become overfit backtest search.
- **Xiao et al. (2025)** — *Trading-R1: Financial Trading with LLM Reasoning* (arXiv:2509.11420, FREE). Reasoning-tuned LLMs applied to trading workflows. Should be treated as experimental until execution cost and live-trading validation are demonstrated.

## Core Theses

### Feature Engineering > Autonomous Execution (GPT-Signal)

LLMs appear more useful as hypothesis generators and feature engineering assistants than as autonomous trading systems. GPT-Signal demonstrates that LLMs can produce creative alpha features when guided by human researchers, but do not claim the LLM itself trades profitably. The human-in-the-loop workflow (LLM suggests → human validates → engineer implements) is the credible path.

### Multi-Agent Architecture Adds Structure, Not Necessarily Alpha (TradingAgents, FinMem, TradingGPT)

Role-separated multi-agent frameworks (researcher, analyst, trader, critic) provide structured processes but do not guarantee the resulting signals have statistical edge. The architecture mimics a human fund's workflow, but mimicking structure does not replicate skill. The key question is whether the decomposition genuinely improves signal quality or merely makes the system more interpretable.

### LLM Behavioral Consistency is the Production Gate (Li et al. 2026)

The critical insight: LLMs are not deterministic systems. Small prompt changes, temperature shifts, or model updates produce meaningfully different trading behavior. An agent that behaves inconsistently is not a trading strategy — it is an uncontrolled random variable. Behavioral consistency validation must be a prerequisite for any production LLM trading system.

### LLM Agents Behave Differently Than Humans Under Trading Incentives (Henning et al. 2025)

Experimental market studies show that LLM agents do not naturally replicate human behavioral biases (disposition effect, overconfidence, etc.). This means LLM agents are not valid stand-ins for human traders in market simulations unless explicitly calibrated — but it also means they avoid the systematic errors that create alpha opportunities (see [[07-01-Behavioral-Finance]]).

### Self-Improvement Risks Overfitting (QuantAgent)

Self-improving LLM agents that iteratively refine trading strategies risk converging on overfit backtest patterns rather than genuine alpha. The self-improvement loop can amplify noise if the evaluation signal (backtest Sharpe, for instance) is itself noisy.

### Agent-Based Simulation is Promising but Unvalidated (Hashimoto 2025, del Rio-Chanona 2025)

LLM-populated market simulations can produce plausible-looking price dynamics and agent interactions, but simulation validity requires behavioral calibration. If LLM agents don't behave like real market participants, the simulation output has no claim to predictive power.

## Implications for Trading Systems

### Credentialed Use Cases

- **Feature/hypothesis generation** (GPT-Signal): Use LLMs to brainstorm feature ideas across data sources, then validate traditionally. This is the most credible current use case.
- **Strategy discovery scaffolding** (Kou 2024): LLMs can enumerate candidate strategy configurations and suggest parameter ranges, but final validation must be independent and rigorous.
- **News sentiment features** (Tetlock legacy + LLM): LLMs can implement Tetlock-style sentiment analysis at scale. The empirical foundation exists (Tetlock 2007), and LLMs are a better implementation tool than dictionary methods.
- **Multi-agent research team simulation**: Role-separated agents can provide diverse perspectives on the same dataset, functioning as a structured adversarial review process that catches groupthink in research teams.

### Architecture Lessons

- **Layered memory** (FinMem, TradingGPT): The concept of short-term, medium-term, and long-term memory layers mirrors how successful systematic strategies use different lookback windows. This concept can be extracted from LLM-specific implementations and applied to traditional ML pipelines.
- **Self-critique loops**: The TradingAgents critic role is essentially a built-in adversarial review. This pattern should be adopted regardless of the LLM component — have one agent/subsystem try to falsify the signals of another.
- **Character/persona design**: Giving agents different risk personalities (conservative, aggressive) can help explore the strategy's Pareto frontier of risk-return configurations.

### Evaluation Standards

- **LiveTradeBench-style testing**: Any LLM trading agent should be evaluated on out-of-sample, live (or paper-live) performance, not backtest results. In-sample and backtest results are meaningless for LLM-generated strategies.
- **Consistency testing** (per Li et al. 2026): Test whether the agent produces the same signal across prompt variations, model temperatures, and minor data perturbations. Inconsistency = not production ready.
- **Behavioral benchmarking** (per Henning et al. 2025): Compare LLM agent behavior to known human biases from behavioral finance. Either you want the agent to exploit those biases or replicate them — but you need to know which.

## Failure Modes

### The Overconfidence Multiplier

LLMs are known to hallucinate with high confidence. In a trading context, a hallucinated signal expressed with high confidence could trigger oversized positions. The Barber-Odean finding (overconfidence → overtrading → losses) is directly applicable to LLM agents. Without position-sizing caps and independent signal validation, LLM overconfidence becomes a financial hazard.

### Prompt Fragility

Trading behavior that depends on specific prompt wording is not robust. A production system cannot assume prompts are stable — models change, system instructions evolve, and context windows shift. Prompt-fragile strategies are operational liabilities.

### Backtest Overfitting via LLM Search

GPT-Signal and QuantAgent both risk creating an LLM-guided walk-forward overfit: the LLM iterates through feature/strategy space guided by noisy backtest signals and converges on patterns with no out-of-sample validity. This is more dangerous than traditional overfitting because the LLM's creativity generates more candidate strategies at higher speed.

### Agent Simulation Illusion

LLM agents in market simulations can produce compelling narratives and plausible price paths, but if the agents' behavioral parameters aren't calibrated to real market participants, the simulation generates fiction, not information. The del Rio-Chanona paper shows that LLM agents don't even reliably reproduce simple human decision-making in generic tasks.

### Model Drift

LLM providers update their models without notice. A trading signal that works with GPT-4 may not work with GPT-4.5. Model drift is a versioning nightmare for any production LLM trading system.

### Multi-Agent Degradation

Adding agents to a system does not linearly improve signal quality. Each agent introduces its own failure modes, and inter-agent communication can create echo chambers or contradictory signals that cancel genuine alpha. The Vidler/Walsh TraderTalk findings suggest agent conversation may add narrative, not signal.

## Anti-Cookie-Cutter Insights

- **LLMs are better at finding features than finding alpha.** The GPT-Signal finding suggests the right workflow is LLM-as-research-assistant, not LLM-as-trader. This inverts the hype.
- **Multi-agent decomposition mimics organizational structure, not skill.** A team of agents playing researcher/analyst/trader/critic doesn't automatically outperform a single good model — it just makes bad decisions more legible.
- **Inconsistency is the killer, not poor accuracy.** An LLM agent that is 55% right but 95% consistent is deployable. An LLM agent that is 70% right but only 60% consistent is not. This inverts the standard ML evaluation mindset.
- **Agent-based market simulations are fiction until behaviorally calibrated.** Plausible-looking price dynamics from LLM agents doesn't mean the simulation has predictive value. It means the LLM is good at generating plausible fiction.

## Cross-Links

- [[07-01-Behavioral-Finance]] — LLM agents should be benchmarked against human behavioral biases; the biases are the alpha source the agents attempt to exploit
- [[07-02-LLM-Trading-Agents]] — Behavioral stability validation is the gatekeeper for any production LLM trading system
- [[TradingAgents Framework]] — Multi-agent architecture reference (researcher/analyst/trader/critic roles)
- [[GPT-Signal]] — Feature engineering workflow: LLM generates hypotheses, humans validate
- [[02-Alpha-Research]] — LLM agents as alpha-research assistants are more credible than autonomous traders
- [[04-Backtesting]] — LLM-generated strategies must survive backtest rigor; overfitting risk is amplified
- [[03-Risk-Management]] — Position sizing caps and drawdown limits are essential for LLM agent safety

## Sources

- `/raw-ingest/quant_research_library/F_llm_trading_agents_multi_agent_orchestration/index.md`
- `/raw-ingest/quant_research_library/F_llm_trading_agents_multi_agent_orchestration/paywalled.md`
