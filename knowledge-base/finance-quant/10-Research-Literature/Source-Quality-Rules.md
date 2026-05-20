# Source Quality Rules

All research and implementation sources must be ranked. Implementation docs: official vendor documentation outranks tutorials.

## Source Ranking

| Rank | Source Type | Examples |
|---|---|---|
| 1 | Peer-reviewed journal or official publisher | RFS, Journal of Finance, CFA Institute |
| 2 | Author personal page / university repository | davidhbailey.com, people.duke.edu/~charvey |
| 3 | NBER / SSRN / arXiv working paper | arxiv.org, ssrn.com |
| 4 | Official framework/vendor documentation | QuantConnect docs, NautilusTrader docs, Alpaca API |
| 5 | High-quality industry whitepaper | Two Sigma tech reports, AQR papers |
| **Reject** | Blogs, SEO farms, piracy mirrors, uncited social posts | Medium tutorials, YouTube descriptions, Sci-Hub |

## Legal Standards

- **Included**: Author personal pages, institutional repositories, NBER/public working paper PDFs, official documentation
- **Excluded**: Sci-Hub, LibGen, piracy mirrors, CAPTCHA-gated files, broken HTML pages renamed as PDFs

## Implications

- When a tutorial contradicts official docs, trust the docs.
- When a blog claims a strategy works, demand the academic source.
- PDFs in the vault come only from verifiable open-access sources.

## Failure Modes

- **Tutorial-as-truth**: blogs often simplify or misrepresent framework behavior.
- **Pirated papers**: illegal to use, and quality cannot be verified.
- **SEO research farms**: papers published on low-tier sites that look academic but lack peer review.
- **Broken HTML as PDF**: some scrapers rename failed HTTP responses as `.pdf` files.

## Cross-Links

- [[Research-Papers-Index]] — all 18 papers sourced from Tier 1-4 sources
- [[Papers-Docs-Synthesis]] — synthesized insights from ranked sources
- [[Trading-System-Build-Doctrine]] — Phase 0 requires Tier 1-2 research
