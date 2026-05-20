# Source Quality & Provenance Assessment

**Purpose**: When selecting research papers or official documentation, know what to trust, what to question, and how to verify claims independently.

---

## Source Tier System

### Tier 1: Peer-Reviewed Academic
- Published in journals like JF, JFE, RFS, Journal of Portfolio Management
- Undergo blind review
- May still be wrong (publication bias favors significant results)
- Examples: Cont (2001), Harvey et al. (2016), Lo et al. (2000)

### Tier 2: Working Papers / Preprints
- arXiv, SSRN, NBER working papers
- Not peer-reviewed but typically credible authors
- Useful for cutting-edge methods but require extra scrutiny
- Examples: Bailey & López de Prado series

### Tier 3: Official Documentation
- Vendor/broker/framework docs
- Authoritative on API behavior but biased toward selling their platform
- Use for implementation details, not for alpha research

### Tier 4: Blog Posts / Tutorials / Forums
- Lowest evidence grade
- May contain practical wisdom but verify independently
- Useful for workflow ideas, not for strategy validation

---

## Verification Checklist
Before using a paper's methodology in a trading system:
- [ ] Are the assumptions stated and realistic for live markets?
- [ ] Was transaction cost modeled reasonably?
- [ ] Was multiple testing addressed?
- [ ] Was out-of-sample validation performed?
- [ ] Is the data free from survivorship and look-ahead bias?
- [ ] Can the methodology be independently reproduced?

---

## Anti-Cookie-Cutter Insight
Many published "factors" fail replication not because academia is wrong, but because:
1. They were tested on data that no longer exists (survivorship)
2. Costs were assumed at institutional levels impossible for retail
3. The methodology requires infrastructure the paper doesn't disclose
4. The effect was real when discovered but has since been arbitraged away

**Rule**: Treat every published factor as a starting point, not a finished strategy.

---

*Cross-linked: [[INDEX-Papers-Docs]], [[Overfit-Detection-Metrics]], [[Trading-System-Build-Doctrine]]*
