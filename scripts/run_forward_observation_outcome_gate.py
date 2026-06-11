from __future__ import annotations

from pathlib import Path

from src.research.meta.outcome_gate import print_gate_result, run_outcome_gate


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    result = run_outcome_gate(ROOT)
    print_gate_result(result)


if __name__ == "__main__":
    main()
