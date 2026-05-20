# D: Model Extraction & Black-Box Reverse Engineering

> Synthesized from Group D of the quant research library. Source: `raw-ingest/quant_research_library/D_model_extraction_black_box_reverse_engineering/`

---

## Key Papers

### Tier 2 — Foundational Model Extraction

1. **Tramer, Zhang, Juels, Reiter & Ristenpart (2016)** — *Stealing Machine Learning Models via Prediction APIs* (USENIX Security, arXiv 1609.02943)
   - Foundational paper: shows how prediction APIs leak enough information through query-response patterns to reconstruct equivalent model behavior
   - Demonstrates that even rate-limited, noisy APIs can be reverse-engineered with sufficient query budget
   - Status: `FREE_DIRECT_PDF`

2. **Papernot, McDaniel, Goodfellow, Jha, Celik & Grama (2017)** — *Practical Black-Box Attacks against Machine Learning* (ACM ASIACCS, arXiv 1602.02697)
   - Develops substitute-model methods: train a local model on API query responses, then attack/optimize the substitute
   - In finance terms: observe market reactions (the "API responses") to your trades and reconstruct latent competitor policies
   - Status: `FREE_DIRECT_PDF`

3. **Krishna, Tomar, Parikh, Papernot & Iyyer (2020)** — *Thieves on Sesame Street! Model Extraction of BERT-based APIs* (ICLR, arXiv 1910.12366)
   - Extraction of behavior from black-box text APIs; directly relevant to monitoring LLM-based competitor agents
   - Shows extraction is feasible even for complex, high-capacity models with appropriate query strategies
   - Status: `FREE_DIRECT_PDF`

### Tier 2 — Modern Advances

4. **Carlini et al. (2024)** — *Stealing Part of a Production Language Model* (arXiv 2403.06634)
   - Demonstrates that partial extraction of production-scale models is practical under specific leakage channels
   - Current-generation: shows the attack surface remains open even for high-capacity, defended systems
   - Status: `FREE_DIRECT_PDF`

5. **Liang et al. (2024)** — *Yes, My LoRD: Lower-Dimensional Subspace Discovery for Efficient Model Extraction* (arXiv 2409.02718)
   - Focuses on extraction efficiency: discovers low-dimensional subspaces of the model's behavior for cheaper extraction
   - Relevant when the observed system (e.g., an institutional trader's execution algorithm) is expensive or limited to observe
   - Status: `FREE_DIRECT_PDF`

---

## Core Theses

- **Black-box behavior is leakable.** Tramer et al. establish that any system you can query (even with rate limits, noise, and access controls) leaks information about its internal decision boundaries. In finance, every observable trade or quote is a "query response" from some participant's internal model.
- **Substitute models are the bridge.** Papernot's substitute-model approach shows you don't need to steal the exact model — you need a model whose behavior matches the original well enough to be useful. In trading, this means you don't need the competitor's exact algorithm, just a behavioral equivalent that predicts their reactions.
- **Extraction is a resource optimization problem.** The Liang paper shows that model extraction can be made efficient by focusing on low-dimensional subspaces. This maps directly to finance: instead of trying to model an entire institutional trading desk, identify the low-dimensional decision manifold they operate on (e.g., volume participation rate, time-slicing schedule, price tolerance bands).
- **Partial extraction is valuable.** Carlini shows you don't need to extract the whole model. Partial extraction of key decision boundaries can be enough to predict behavior in the regimes that matter for your strategy.
- **LLM agents are extractable.** Krishna et al. demonstrate that even complex language-based agents leak behavioral patterns. This directly applies to LLM trading agents and multi-agent systems, which are increasingly used in quantitative settings.

---

## Implications for Trading Systems

- **Substitute-model framework for institutional behavior.** Treat each observed market participant (market maker, execution algo, CTA, institutional flow) as a black-box model. Use substitute-model methods (Papernot) to train local models that predict their behavior given market state inputs. The "queries" are market events you observe; the "responses" are their subsequent trades/quotes.
- **Low-dimensional extraction for execution prediction.** Use the LoRD subspace-discovery approach (Liang et al.) to identify the key decision dimensions of execution algorithms. Most execution algos operate on a low-dimensional manifold: participation rate, urgency, spread tolerance, and TWAP/VWAP schedule. Extract these dimensions from observed trade sequences rather than trying to model the full decision process.
- **Competitor-agent monitoring.** The Krishna et al. and Carlini results imply that LLM-based trading agents can be monitored and their decision patterns extracted from their market activity. This creates a new category of signal: inferred agent policies from competitor LLM outputs.
- **Partial extraction for regime-specific prediction.** You don't need to extract a full policy. Extract only the decision boundaries relevant to the regimes your strategy trades (e.g., high-volatility opening, low-volatility lunch period). This is computationally cheaper and more accurate than full extraction.
- **Rate-limited observation is sufficient.** The Tramer paper shows that even limited query budgets (rate-limited API access) are enough for extraction. In markets, you naturally have rate-limited observations (discrete trade data, periodic disclosures). The extraction methods work under exactly these constraints.

---

## Failure Modes

- **The target is actively defending.** Model extraction in security assumes a defender trying to prevent extraction. In finance, if a market participant realizes you're inferring their policy, they will change their behavior — either randomly, adversarially, or by using decoy strategies. This makes the extracted model obsolete.
- **Non-stationary targets.** Unlike a static ML API, trading strategies change with market regimes, risk budgets, and competitive dynamics. An extracted model decays continuously. The extraction must be treated as a continuous inference process, not a one-time attack.
- **Signal-to-noise in market data is terrible.** Prediction APIs give clean, structured outputs. Market observations are noisy, confounded by other participants' actions, and contaminated by random noise trading. The extraction signal-to-noise ratio is orders of magnitude worse than in the ML security setting.
- **Confounded observations.** When you observe a trade, you don't know if it comes from the agent you're modeling or from another participant. In security, the API response comes from one model. In markets, the "output" is an aggregate of many participants' actions. De-conflicting this requires strong assumptions about participant identity or timing.
- **No ground truth for validation.** In the ML extraction setting, you can evaluate extraction by comparing your substitute's outputs to the original API. In markets, there is no ground truth — you don't have access to the true decision function you're trying to extract. Your only validation is predictive accuracy on future behavior, which confounds extraction quality with market unpredictability.

---

## Anti-Cookie-Cutter Insight

**ICT (Inner Circle Trader) and similar retail "smart money concepts" have zero academic support.** The model-extraction literature in Group D provides the closest rigorous analogue to what ICT practitioners claim to do: reverse-engineer institutional decision logic from observable market behavior (order blocks, liquidity pools, fair value gaps). However, the academic literature shows that real model extraction requires (a) structured query-response data, (b) identifiable observation channels, and (c) systematic evaluation against ground truth. ICT's pattern-matching approach provides none of these — it is post-hoc visual pattern matching without the formal framework. The rigorous approach is to use substitute-model methods + low-dimensional subspace discovery (LoRD) + continuous re-inference. Anything less is pattern-fitting with a financial astrology flavor.

---

## Cross-Links

- [[B-Inverse-Reinforcement-Learning-in-Finance]] — IRL is the behavioral analogue of model extraction: both recover latent decision logic from observed behavior, but IRL assumes MDP structure while extraction is model-agnostic
- [[C-Foundational-IRL-Imitation-Learning]] — GAIL/AIRL adversarial training connects to substitute-model methods; both use discriminators to distinguish real from synthetic behavior
- [[A-Reverse-Engineering-Investor-Decision-Logic]] — Demand systems provide a structural approach to the same goal (inferring investor decision logic) but using econometrics rather than black-box extraction
- [[07-02-LLM-Trading-Agents]] — LLM agent extraction (Krishna et al., Carlini et al.) directly applies to monitoring competitor LLM trading agents

---

*Created: 2026-05-17 | Source: Groups D research library | Status: Synthesized*
