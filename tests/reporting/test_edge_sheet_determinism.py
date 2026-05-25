from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "generate_edge_sheet.py"
EDGE_DIR = ROOT / "reports" / "edge_sheet"


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _run_generator() -> None:
    result = subprocess.run(
        [str(ROOT / ".venv/bin/python"), str(SCRIPT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(ROOT)},
    )
    assert result.returncode == 0, result.stdout + result.stderr


def _normalized_json_bytes(path: Path) -> bytes:
    payload = json.loads(path.read_text())
    payload["generated_at"] = "<normalized>"
    if isinstance(payload.get("scoreboard"), dict):
        payload["scoreboard"]["generated_at"] = "<normalized>"
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_repeated_generation_is_deterministic_for_same_input_ledgers():
    _run_generator()

    d = _today()
    md_path = EDGE_DIR / f"{d}_edge_sheet.md"
    json_path = EDGE_DIR / f"{d}_edge_sheet.json"
    score_md_path = EDGE_DIR / f"{d}_scoreboard.md"
    score_json_path = EDGE_DIR / f"{d}_scoreboard.json"

    before = {
        "md": _sha(md_path.read_bytes()),
        "json": _sha(_normalized_json_bytes(json_path)),
        "score_md": _sha(score_md_path.read_bytes()),
        "score_json": _sha(_normalized_json_bytes(score_json_path)),
    }

    _run_generator()

    after = {
        "md": _sha(md_path.read_bytes()),
        "json": _sha(_normalized_json_bytes(json_path)),
        "score_md": _sha(score_md_path.read_bytes()),
        "score_json": _sha(_normalized_json_bytes(score_json_path)),
    }

    assert before == after
