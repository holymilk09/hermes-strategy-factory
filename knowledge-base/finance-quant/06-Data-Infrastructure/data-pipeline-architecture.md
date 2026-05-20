# Data Pipeline Architecture

## Key Concepts

### Three Data Paths

| Path | Use | Required Controls |
|---|---|---|
| Historical Research | Hypothesis discovery, exploration | Raw snapshots, point-in-time features, anti-leakage rules |
| Backtest Feed | Deterministic simulation | Fixed data version, calendar, corporate actions, symbol map |
| Live Feed | Execution and monitoring | Heartbeat, latency checks, stale-data policy, reconnection |

### Canonical Pipeline Stages

```
vendor adapter → raw store → schema validator → timestamp normalizer → symbol mapper → corporate-action adjuster → bar/tick/book aggregator → quality checker → feature calculator → point-in-time feature store → backtest/live consumer
```

Every stage transforms data; none should mutate in place on the raw layer. The pipeline is **append-only** for raw data, **versioned** for normalized data, and **timestamped** for features.

### Storage Design Principles

- **Raw vendor payloads**: immutable — never overwrite
- **Normalized data**: versioned with explicit hash or commit
- **Features**: timestamped and point-in-time auditable
- **Run data**: linked to `data_version` and `feature_version`
- **Quality reports**: stored per dataset and per run

### Historical Data Traps

Common failure sources that destroy backtest validity:

- Split-adjusted OHLCV mixed with raw trades
- Vendor survivorship filters silently removing delisted names
- Ticker reuse (new company inherits old ticker symbol)
- Delisting omissions
- Time zone shift at daylight savings boundaries
- Futures continuous-contract roll logic not recorded
- Options chain snapshots missing expired contracts
- Crypto exchange outages hidden by resampled bars

### Live Feed Requirements

A live feed must maintain: heartbeat per venue, last-message timestamp, market-data latency measurement, stale-data threshold, reconnect policy, replay-safe event ordering, duplicate handling, and out-of-order handling.

**Live action policy** — what the system does under each data condition:

| Data Condition | Action |
|---|---|
| Feed delayed but under threshold | Continue, log warning |
| Feed stale over threshold | Block new entries |
| Feed disconnected | Cancel unsafe open orders per risk policy |
| Feed recovered | Reconcile state before new orders |
| Out-of-order data | Reject event or reorder deterministically |
| Price spike beyond guardrail | Require secondary validation or risk veto |

### Live/Research Parity

Use the same feature calculation code for backtest and live. The only difference should be the data adapter and execution adapter. This is the single most important rule for preventing live trading surprises.

### Dataset Version Naming Convention

```
assetclass_vendor_dataset_adjustment_calendar_start_end_hash
example: us_equity_databento_ohlcv_splitdivadj_nyse_20150101_20251231_ab12cd
```

### Mandatory Metadata Per Dataset

Source vendor, dataset name, ingest timestamp, market timestamp, time zone, symbol format, adjustment method, data version/hash, missing-data flags, corporate-action version.

## Implications for Real Trading Systems

- **Raw-immutable, normalized-versioned**: without this, you can never reproduce a backtest or audit why a live trade happened
- **Separate historical, backtest, and live paths**: they have different requirements; sharing code without sharing state assumptions causes live failures
- **Live/research parity is non-negotiable**: the most common live loss scenario is "the backtest used different data than live"
- **Quality gates before feature calculation**: garbage data → garbage features → garbage signals → garbage trades. Check quality first
- **Stale-data thresholds must be tight**: in live trading, stale data is worse than no data — it creates false confidence

## Failure Modes

- **Mixed adjustment policies**: using split-adjusted prices for one calculation and raw prices for another creates phantom returns
- **Timestamp zone confusion**: treating UTC timestamps as local (or vice versa) shifts signals into the future
- **Corporate action gaps**: failing to apply splits/dividends consistently creates return discontinuities
- **Missing live reconnect logic**: after API disconnection, the system resumes trading on stale positions
- **Version drift**: backtest runs on v3 data while live uses v4 — results diverge with no clear cause

## Cross-Links

- [[Data Quality Checks]] — the quality gate that feeds into the pipeline after the quality checker stage
- [[Feature Store Design]] — how features are cataloged, versioned, and served after the feature calculator
- [[Feature Leakage Prevention]] — point-in-time rules that guard every stage of this pipeline
- [[Schema Catalog]] — JSON schemas for bar, signal, order, fill, market event, backtest run, and model epoch
- [[Fill and Transaction Cost Models]] — cost modeling that sits between the execution simulator and the fill
- [[Backtest Architecture]] — how the backtest feed connects to the event-driven engine
- [[Logging-Audit-Monitoring]] — the lineage chain from raw data hash through to production fills
