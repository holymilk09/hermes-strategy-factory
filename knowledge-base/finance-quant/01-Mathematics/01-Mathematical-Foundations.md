# Mathematics Foundations for Quantitative Trading

**Purpose**: Core mathematical frameworks that underpin strategy design, risk management, and alpha generation. These are not academic exercises — every concept has direct trading system implications.

---

## 01. Linear Algebra for Finance

### Key Concepts
- **Eigenvalues/Eigenvectors**: Principal component analysis for factor decomposition, portfolio risk attribution
- **SVD/PCA**: Dimensionality reduction for cross-sectional factor models, noise filtering
- **Matrix Conditioning**: Ill-conditioned covariance matrices break portfolio optimization; requires regularization (Ledoit-Wolf shrinkage)
- **Quadratic Forms**: Portfolio variance = w'Σw; the geometry of risk is ellipsoidal

### Trading Implications
- Risk parity and HRP use eigen-decomposition of covariance/correlation matrices
- Factor models (Fama-French, statistical factors) are linear projections onto factor space
- Kelly criterion requires solving w* = Σ⁻¹μ — inverse covariance is the critical operation

### Failure Modes
- Inverting near-singular covariance matrices → unstable portfolios
- Ignoring matrix conditioning → optimization exploits noise, not signal

### Cross-Links
- [[Feature-Engineering-Catalog]] — PCA factor models
- [[Risk-Metrics]] — Covariance estimation, portfolio variance
- [[ML-Asset-Pricing-Synthesis]] — IPCA (Instrumented PCA), deep partial least squares

---

## 02. Stochastic Calculus

### Key Concepts
- **Brownian Motion**: W(t) — continuous-time random walk with independent increments, zero drift
- **Itô's Lemma**: dF(X,t) = (∂F/∂t)dt + (∂F/∂X)dX + ½(∂²F/∂X²)dX² — change of variables for stochastic processes
- **Stochastic Differential Equations**: dS = μS dt + σS dW — geometric Brownian motion baseline
- **Martingales**: E[S(t+1)|F_t] = S(t) — fair game; risk-neutral pricing assumes discounted prices are martingales
- **Girsanov's Theorem**: Change of measure from physical to risk-neutral — foundation of derivatives pricing

### Trading Implications
- Options pricing (Black-Scholes, Heston) requires Itô calculus
- Pairs trading mean reversion modeled as Ornstein-Uhlenbeck process
- Volatility surface modeling requires understanding of stochastic vol processes
- HFT order flow modeled as Hawkes processes (self-exciting point processes)

### Failure Modes
- Assuming GBM for returns (ignores fat tails, jumps, volatility clustering)
- Calibrating models on wrong measure (P vs Q confusion)
- Using continuous-time models on discrete data without correction

### Cross-Links
- [[Options-Volatility-Synthesis]] — Black-Scholes, Heston, local vol
- [[08-Market-Microstructure-LOB-Execution-Synthesis]] — Almgren-Chriss (calculus of variations)
- [[08-RL-Deep-Direct-RL-Portfolio-Management]] — Diffusion models for portfolio trajectories

---

## 03. Optimization & Convexity

### Key Concepts
- **Convex Optimization**: Guaranteed global minimum, efficient solvers (CVXOPT, scipy)
- **Quadratic Programming**: Mean-variance optimization, portfolio construction with constraints
- **Lagrangian Multipliers**: Constrained optimization (budget, leverage, long-only constraints)
- **Non-Convex Problems**: Neural network training, RL — multiple local minima, no guarantees
- **Regularization**: L1 (Lasso/feature selection), L2 (Ridge/weight stability), Elastic Net

### Trading Implications
- Portfolio construction: min w'Σw - λw'μ subject to constraints → QP
- Risk parity: vol contribution equalization → non-linear optimization
- L1 regularization in factor models → sparse, interpretable signals
- Gradient-based training in ML strategies → non-convex, requires careful initialization

### Failure Modes
- Unconstrained portfolio optimization → extreme concentrations
- Non-convex optimization without multiple restarts → local minimum masquerading as global
- Over-regularization → underfitting; under-regularization → overfitting

### Cross-Links
- [[ML-Asset-Pricing-Synthesis]] — Ridge/Lasso factor models, regularization
- [[Risk-Metrics]] — Portfolio optimization, risk parity
- [[05-Failure-Mode-Catalog]] — Model risk, overfitting

---

## 04. Information Theory

### Key Concepts
- **Shannon Entropy**: H(X) = -Σ p(x) log p(x) — measure of uncertainty
- **Mutual Information**: I(X;Y) = H(X) - H(X|Y) — predictive relationship strength, captures non-linear dependencies
- **KL Divergence**: D_KL(P||Q) — distance between distributions; regime detection via distribution shifts
- **Cross-Entropy**: Classification loss in ML strategies

### Trading Implications
- Feature selection: maximize MI(feature, return) — captures non-linear predictive relationships that correlation misses
- Regime detection: KL divergence between rolling distributions — identifies when market state has changed
- Portfolio diversification: maximum entropy weight allocation — least concentrated portfolio given return estimates
- Model evaluation: cross-entropy loss for direction classification

### Failure Modes
- Estimating entropy/MI from small samples → unreliable, biased upward
- KL divergence sensitive to zero-probability events → requires smoothing
- Maximum entropy portfolios can still have high risk if return estimates are wrong

### Cross-Links
- [[Feature-Engineering-Catalog]] — Information-based feature selection
- [[Feature-Leakage-Prevention]] — MI leakage tests
- [[Risk-Statistical-Modeling-Synthesis]] — Distribution analysis, stylized facts

---

## 05. Fractal Geometry & Market Scaling

### Key Concepts
- **Hurst Exponent**: H > 0.5 (trending), H = 0.5 (random walk), H < 0.5 (mean-reverting)
- **Fractal Dimension**: Market price paths are not smooth — they have fractal dimension ~1.5-1.7
- **Multifractal Models**: Different scaling properties at different time scales; captures volatility clustering
- **Scaling Laws**: Volatility scales as √T under Brownian assumption; deviations indicate structure

### Trading Implications
- Trend detection: H > 0.5 over rolling windows signals trending regime
- Mean reversion: H < 0.5 signals short-term reversibility
- Time horizon selection: if market exhibits multifractal scaling, different strategies work at different scales
- Volatility forecasting: multifractal models (Mandalbrot, Calvet-Fisher) capture vol clustering

### Failure Modes
- Estimating H from short windows → unreliable, confounded by regime shifts
- Assuming constant Hurst exponent → markets shift between regimes
- Fractal models descriptive, not predictive — knowing H=0.6 doesn't predict direction

### Cross-Links
- [[Feature-Engineering-Catalog]] — Regime features, scaling features
- [[08-Market-Microstructure-LOB-Execution-Synthesis]] — Price impact scaling
- [[01-Pattern-Recognition-Synthesis]] — Agent-based market dynamics

---

## Mathematical Anti-Cookie-Cutter Insights

1. **Linear algebra is the bottleneck for portfolio optimization**. A portfolio optimizer is only as good as its covariance matrix estimate. Garbage in → garbage out. Most "sophisticated" portfolio construction fails because Σ is estimated poorly, not because the optimizer is wrong.

2. **Stochastic calculus models are beautiful but wrong**. GBM assumes independent increments and constant volatility. Real markets exhibit dependence, jumps, and volatility clustering. Use models as approximations, not descriptions of reality.

3. **Convexity separates tractable from intractable**. If your trading problem can be formulated as convex optimization, you can solve it. If not (e.g., RL, neural nets), you're navigating a landscape of local minima with no guarantees.

4. **Information theory finds signals correlation misses**. Linear correlation captures only linear relationships. Mutual information discovers non-linear predictive relationships that standard feature selection overlooks.

5. **Fractal scaling explains why "optimal holding period" is asset-specific**. If returns don't scale as √T (and they often don't), the assumption that vol targeting works at all timeframes is wrong.

---

*Cross-linked: [[Risk-Metrics]], [[Feature-Engineering-Catalog]], [[ML-Asset-Pricing-Synthesis]], [[Options-Volatility-Synthesis]], [[08-RL-Deep-Direct-RL-Portfolio-Management]], [[08-Market-Microstructure-LOB-Execution-Synthesis]], [[01-Pattern-Recognition-Synthesis]]*
