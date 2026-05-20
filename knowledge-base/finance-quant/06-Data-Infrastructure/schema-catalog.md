# Schema Catalog

Consolidated reference for all event schemas used in the quant data pipeline. Schemas define the contract between pipeline stages and ensure full auditability.

<!--
Note: These schemas are derived from JSON schema source files.
Originals in raw-ingest: 01_data_pipelines/schemas/
-->

## Bar Schema

OHLCV price bar with optional adjustment policy.

**Required fields**: symbol, timestamp, open, high, low, close, volume
**Optional fields**: adjustment_policy

All numeric fields are numbers. Timestamp is ISO 8601 date-time.

## Market Event Schema

Typed market events flowing through the event queue.

**Required fields**: event_id, symbol, timestamp, source, event_type
**Optional fields**: quality_flags (array of strings)
**event_type enum**: bar, trade, quote, book, fundamental, macro

## Signal Schema

Strategy output consumed by the portfolio/risk layer.

**Required fields**: run_id, symbol, timestamp, strategy_id, score, horizon, reason_codes (array of strings)
**Optional fields**: direction (long/short/flat), confidence (number)

## Order Instruction Schema

Order sent to the broker/execution adapter.

**Required fields**: client_order_id, symbol, side (buy/sell), quantity, order_type, time_in_force
**Optional fields**: limit_price (number or null), risk_approval_id
**order_type enum**: market, limit, stop, stop_limit, trailing_stop

## Fill Schema

Execution result from the broker or fill model.

**Required fields**: client_order_id, symbol, timestamp, side (buy/sell), quantity, fill_price, fees
**Optional fields**: venue

## Backtest Run Schema

Run identity and results container.

**Required fields**: run_id, strategy_id, config_hash, data_version, start (date), end (date), metrics (object)

## Model Epoch Schema

Train/validate/test windows with promotion decision for the epoch learning loop.

**Required fields**: epoch_id, train_start, train_end, validation_start, validation_end, test_start, test_end (all date), promotion_decision (promote/reject/hold)

## Cross-Links

- [[Data Pipeline Architecture]] — schemas define the interface between pipeline stages (ingest → validate → feature compute → signal emit → order → fill)
- [[Logging-Audit-Monitoring]] — the lineage chain hashes each schema-conformed artifact; run manifests store all hashes
- [[Testing Strategy]] — contract tests validate that each module produces schema-conforming output
- [[Logging Contract]] — log entries reference the schema type of their payload
- [[Feature Store Design]] — feature versioning tracks which schema version each feature depends on
