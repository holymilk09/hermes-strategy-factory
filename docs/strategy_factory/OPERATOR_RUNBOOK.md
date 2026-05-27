# Strategy Factory — Daily Operator Runbook

Updated: 2026-05-27
Asset: Hermes Strategy Factory
Branch: trust-calibration-working (currently)

## Schedule

| Period | Action |
|---|---|
| Market open — close | No action |
| After market close (~6 PM ET) | Run daily maturity update |

## Daily After-Market Procedure

```bash
cd /opt/data
source .venv/bin/activate
export PYTHONPATH=.
```

**1. Refresh completed daily OHLCV bars**

```bash
python3 scripts/tmp_download_ohlcv.py
```

If yfinance returns no new bars (weekend/holiday), skip. Verify with:

```bash
# Check max bar date
tail -1 data/cache/ohlcv_1d/SPY_1D.csv | cut -d, -f1
```

**2. Run canonical forward observation scripts**

```bash
python scripts/run_relative_strength_observation_cycle.py
```

**3. Run maturity watchdog**

```bash
python scripts/show_relative_strength_maturity_watchdog.py
```

**4. Run ghost recording** (append-only, idempotent)

Ghost recording runs as part of `run_relative_strength_forward_observation_once.py` (called by the observation cycle). No separate invocation needed.

**5. Run trust calibration audit** (if applicable)

```bash
python scripts/run_trust_calibration_audit.py
```

Only generates trust state reports if completed outcomes exist. Currently all outcomes pending.

**6. Run reporting tests**

```bash
PYTHONPATH=/opt/data /opt/data/.venv/bin/pytest -q tests/reporting
```

Expected: 70 passed.

**7. Run healthcheck**

```bash
PYTHONPATH=/opt/data /opt/data/.venv/bin/python scripts/run_feature_factory_healthcheck.py
```

Expected: HEALTHCHECK_PASS_CONTINUE_WAITING

**8. Produce compact daily maturity report**

Deliver in compact format:

Branch: trust-calibration-working
Commit: b8280d7
Ahead/behind: 0/0
Observations: 6 pending / 0 matured
Future bars: 3/10
Bars remaining: 7
Next expected maturity: ~June 3
New observations: 0
Ghost records total: 12
New ghost records: 6
Rejection reasons: 20d_momentum (10), 60d_momentum (2)
Trust calibration: No completed outcomes
Filter impact: INCONCLUSIVE
Healthcheck: PASS_CONTINUE_WAITING
Production/live/broker/shadow: ALL BLOCKED
Strategy changes: NO
Threshold changes: NO
Scoring changes: NO
Maturity changes: NO
Broker/live/shadow changes: NO
No new feature work.

## Required Report Fields

- branch
- commit
- ahead/behind
- observations total
- pending
- resolved/matured
- future bars / bars remaining / next expected maturity
- new observations written
- ghost record total / new ghost records
- rejection reasons recorded
- trust calibration status
- filter impact status
- healthcheck result
- production/live/broker/shadow block status
- safety confirmations (5 "NO" statements)

## Safety Rules

- Do not change strategy logic.
- Do not change thresholds.
- Do not change scoring.
- Do not change features.
- Do not change maturity rules.
- Do not touch broker/live/shadow/production.
- Do not stage, commit, push, merge, rebase, reset, or clean during daily run.
- Allow ghost recording to run silently (append-only audit instrumentation).