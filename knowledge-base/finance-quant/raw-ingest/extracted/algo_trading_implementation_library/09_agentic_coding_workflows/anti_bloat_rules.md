# Anti-Bloat Rules

## File creation rule

Create a new file only if:

- It represents a new module boundary.
- Existing files would become mixed-purpose.
- The file is a required output artifact.

## Do not create

- `strategy_new.py`
- `strategy_final.py`
- `strategy_working.py`
- `metrics2.py`
- `backtest_fixed.py`
- `utils_temp.py`

## Refactor rule

No broad refactor while debugging a strategy. First find the failing invariant.
