from __future__ import annotations

from pathlib import Path

from src.paper.observation_cycle import read_observation_status


ROOT = Path(__file__).resolve().parents[1]

OBS_DIR = ROOT / "data" / "paper_observation"

OBS_LEDGER = OBS_DIR / "regime_conditioned_capitulation_v2_observation_ledger.csv"
OUTCOME_LEDGER = OBS_DIR / "regime_conditioned_capitulation_v2_outcome_ledger.csv"


def main() -> None:
    status = read_observation_status(
        observation_ledger=OBS_LEDGER,
        outcome_ledger=OUTCOME_LEDGER,
    )

    print("=== FORWARD OBSERVATION STATUS ===")
    for k, v in status.items():
        print(f"{k}: {v}")
    print("Production: BLOCKED")
    print("Live: BLOCKED")
    print("Broker execution: DISABLED")
    print("Shadow orders: DISABLED")


if __name__ == "__main__":
    main()
