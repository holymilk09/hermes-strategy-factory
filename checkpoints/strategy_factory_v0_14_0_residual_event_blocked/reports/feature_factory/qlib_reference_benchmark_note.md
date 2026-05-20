# Qlib Reference Benchmark Note

Status: REFERENCE_ONLY — no migration, no installation, no rewrite.

## Architecture Mapping

| Hermes Component | Qlib Equivalent |
|---|---|
| Hermes RawDataStore (Alpaca→NPZ) | Qlib Data Layer |
| Hermes FeatureFactory | Qlib DataHandler / Alpha158-style handler |
| Hermes FeatureDataset | Qlib Dataset |
| Hermes LabelFactory | Qlib Label Config |
| Hermes Validation Reports | Qlib Recorder / Signal Analysis |
| Hermes Strategy Integration | Qlib Strategy / Executor |

## Current Position

Qlib is useful now as an architecture and benchmark reference. Hermes should NOT rewrite into Qlib during current validation.

## Optional Future Benchmark

- Create Qlib-style Alpha158 compatibility adapter after current Phase 4.5 audit completes.
- Compare Hermes feature sets vs Alpha158-style baseline on same universe, labels, purged CV, and cost proxy.
- Do not run this until current signal sanity audit is complete.

## Forbidden Actions

- No Qlib migration
- No Qlib dependency injection
- No Qlib rewrite
- No replacing Hermes validation reports
- No installing broad new alpha-mining toolchains during this phase
