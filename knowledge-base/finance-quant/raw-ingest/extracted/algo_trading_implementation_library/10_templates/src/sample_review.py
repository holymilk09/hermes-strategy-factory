from __future__ import annotations


def classify_weak_points(metrics: dict) -> list[dict]:
    weak = []
    if metrics.get("sharpe", 0) < 1.0:
        weak.append({"category": "performance", "issue": "Sharpe below threshold", "severity": "medium"})
    if metrics.get("max_drawdown", 0) < -0.15:
        weak.append({"category": "risk", "issue": "Max drawdown too deep", "severity": "high"})
    if metrics.get("profit_factor", 0) < 1.2:
        weak.append({"category": "trade_quality", "issue": "Profit factor weak", "severity": "medium"})
    if metrics.get("time_under_water", 0) > 0.65:
        weak.append({"category": "deployability", "issue": "Too much time under water", "severity": "medium"})
    return weak
