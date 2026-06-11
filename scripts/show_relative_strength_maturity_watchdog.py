from __future__ import annotations

from pathlib import Path

from src.paper.maturity_watchdog import (
    compute_maturity_status,
    write_watchdog_reports,
)


ROOT = Path(__file__).resolve().parents[1]

OBS_LEDGER = (
    ROOT
    / "data"
    / "paper_observation"
    / "relative_strength_continuation_observation_ledger.csv"
)

REPORT_MD = (
    ROOT
    / "reports"
    / "strategy_factory"
    / "relative_strength_maturity_watchdog.md"
)
REPORT_JSON = (
    ROOT
    / "reports"
    / "strategy_factory"
    / "relative_strength_maturity_watchdog.json"
)


def main() -> None:
    result = compute_maturity_status(
        root=ROOT,
        observation_ledger=OBS_LEDGER,
    )

    write_watchdog_reports(
        result=result,
        markdown_path=REPORT_MD,
        json_path=REPORT_JSON,
    )

    if result["classification"] == "WATCHDOG_HARD_FAIL_BROKER_FLAG":
        raise RuntimeError("Broker flag detected in observation ledger")

    print("=== PHASE 30E MATURITY WATCHDOG COMPLETE ===")
    print(f"Classification: {result['classification']}")
    print(f"Observations total: {result.get('observations_total')}")
    print(f"Mature count: {result.get('mature_count')}")
    print(f"Pending count: {result.get('pending_count')}")
    print(f"All mature: {result.get('all_mature')}")
    print(f"Ready for outcome update: {result.get('ready_for_outcome_update')}")
    print("")

    for row in result.get("rows", []):
        print(
            f"{row['symbol']}: "
            f"future_bars={row['future_bars']} "
            f"bars_remaining={row['bars_remaining']} "
            f"mature={row['mature']} "
            f"latest_ohlcv_ts={row['latest_ohlcv_ts']}"
        )

    print("")
    print(f"Report: {REPORT_MD}")
    print(f"JSON: {REPORT_JSON}")
    print("Production: BLOCKED")
    print("Live: BLOCKED")
    print("Broker execution: DISABLED")
    print("Shadow orders: DISABLED")


if __name__ == "__main__":
    main()
