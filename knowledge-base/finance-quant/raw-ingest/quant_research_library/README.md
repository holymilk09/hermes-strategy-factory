# quant_research_library

Generated: 2026-05-16T05:49:19Z

This package is an organized research-library scaffold for reverse-engineering trader/investor decision logic, quantitative trading, ML asset pricing, IRL, LLM trading agents, market microstructure, options, risk, technical-analysis evidence, prediction markets, hedge-fund/13F literature, and market pattern recognition.

## Important limitation

Actual PDFs are not embedded in this zip. Direct filesystem downloads failed in this environment due to DNS resolution failure during live download attempts. Browser-side source verification was possible for a subset of official pages, but saving PDF bytes locally was not possible here.

The package therefore includes:

- One subfolder per topic group A-R.
- `index.md` and `paywalled.md` for every group.
- `MASTER_INDEX.md` across all groups.
- `READ_ORDER.md` for a technical founder building algorithmic trading systems.
- `SYNTHESIS.md` mapping intellectual lineages and open research questions.
- `DOWNLOAD_MANIFEST.csv` containing legal direct PDF URLs where captured.
- `download_open_pdfs.py`, a local downloader and validator.
- `metadata.json` with structured records.

## How to download PDFs locally

Run from the top-level folder:

```bash
python3 download_open_pdfs.py
```

The script downloads only rows with direct legal PDF URLs in `DOWNLOAD_MANIFEST.csv`, writes files into each group's `papers/` folder, validates the `%PDF-` header, and writes `DOWNLOAD_RESULTS.csv`.

## Source-quality policy

Priority order used:

1. Peer-reviewed journal or top conference.
2. NBER, SSRN, university/institutional working paper.
3. arXiv/preprint.
4. High-quality industry report from known firms or institutions.
5. Books or sample chapters where the full work is paid.

No Sci-Hub, LibGen, pirated mirrors, Medium posts, SEO content farms, or informal blogs are included.

## Abstract handling

The `abstract_summary` fields are paraphrased research summaries, not verbatim abstracts. This avoids embedding long copyrighted abstracts while still preserving the paper's relevance.
