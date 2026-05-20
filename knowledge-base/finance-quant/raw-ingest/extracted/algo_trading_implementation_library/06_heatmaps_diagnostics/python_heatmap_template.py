'''Heatmap template for parameter diagnostics.

Usage:
    python python_heatmap_template.py sample_parameter_grid.csv sharpe

Notes:
    - Uses matplotlib only.
    - Does not set custom colors.
'''
from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def plot_heatmap(csv_path: str, metric: str = "sharpe") -> None:
    df = pd.read_csv(csv_path)
    required = {"fast_ma", "slow_ma", metric}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    grid = df.pivot(index="fast_ma", columns="slow_ma", values=metric)
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(grid.values, aspect="auto")
    ax.set_xticks(range(len(grid.columns)))
    ax.set_xticklabels(grid.columns)
    ax.set_yticks(range(len(grid.index)))
    ax.set_yticklabels(grid.index)
    ax.set_xlabel("slow_ma")
    ax.set_ylabel("fast_ma")
    ax.set_title(f"Parameter heatmap: {metric}")
    fig.colorbar(im, ax=ax)
    out = Path(csv_path).with_suffix(f".{metric}.heatmap.png")
    fig.tight_layout()
    fig.savefig(out, dpi=160)
    print(f"Saved {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python python_heatmap_template.py sample_parameter_grid.csv [metric]")
    plot_heatmap(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "sharpe")
