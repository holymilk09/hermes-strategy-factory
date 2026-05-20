# Codex / Cursor / Windsurf Guardrails

## Prompt rule

The agent should never be asked to “make it profitable.” Ask it to implement a specified test, metric, or diagnostic.

## Good prompt

> Implement the `max_drawdown` and `time_under_water` metrics in `src/core/metrics.py`. Add unit tests using the equity curve fixture. Do not modify strategy code.

## Bad prompt

> Improve the strategy and find better parameters.

## Anti-bloat command

> Before writing code, list the existing files you will modify. Do not create new files unless no existing file fits the change.
