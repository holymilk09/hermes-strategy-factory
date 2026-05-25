#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from src.reporting.edge_sheet_html import render_from_paths

ROOT = Path("/opt/data")
REPORT_DIR = ROOT / "reports" / "edge_sheet"


def main() -> None:
    as_of = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    edge_json = REPORT_DIR / f"{as_of}_edge_sheet.json"
    score_json = REPORT_DIR / f"{as_of}_scoreboard.json"

    if not edge_json.exists() or not score_json.exists():
        raise SystemExit("Missing input JSON artifacts. Run generate_edge_sheet.py first.")

    rendered = render_from_paths(edge_json, score_json)

    edge_html_path = REPORT_DIR / f"{as_of}_edge_sheet.html"
    score_html_path = REPORT_DIR / f"{as_of}_scoreboard.html"
    preview_html_path = REPORT_DIR / f"{as_of}_email_preview.html"

    edge_html_path.write_text(rendered["edge_html"])
    score_html_path.write_text(rendered["scoreboard_html"])
    preview_html_path.write_text(rendered["email_preview_html"])

    print("=== EDGE SHEET HTML RENDERED ===")
    print(f"edge_html={edge_html_path}")
    print(f"scoreboard_html={score_html_path}")
    print(f"email_preview_html={preview_html_path}")
    print("Rendering-only phase complete. No strategy behavior changed.")


if __name__ == "__main__":
    main()
