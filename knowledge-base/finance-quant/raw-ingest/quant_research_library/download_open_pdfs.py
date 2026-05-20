#!/usr/bin/env python3
"""
Download legal/open PDFs listed in DOWNLOAD_MANIFEST.csv.

Rules enforced:
- Uses only captured official or primary-source direct PDF URLs.
- Writes each file to the group/papers folder.
- Validates PDF header starts with %PDF- and file size is non-trivial.
- Does not use copyright-circumvention sources.
"""
from __future__ import annotations
import csv
import os
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "DOWNLOAD_MANIFEST.csv"
RESULTS = ROOT / "DOWNLOAD_RESULTS.csv"
MIN_BYTES = 20_000
TIMEOUT = 45

HEADERS = {
    "User-Agent": "quant-research-library-downloader/1.0 (+legal-open-access-only)"
}

def fetch(url: str, dest: Path) -> tuple[str, str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read()
        if len(data) < MIN_BYTES:
            return "FAIL", f"too small: {len(data)} bytes"
        if not data.startswith(b"%PDF-"):
            prefix = data[:80].decode("latin-1", errors="replace").replace("\n", " ")
            return "FAIL", f"not PDF header; first bytes={prefix!r}"
        tmp.write_bytes(data)
        tmp.replace(dest)
        return "OK", f"{len(data)} bytes"
    except Exception as e:
        return "FAIL", f"{type(e).__name__}: {e}"


def main() -> None:
    rows = list(csv.DictReader(MANIFEST.open(newline='', encoding='utf-8')))
    # Keep deterministic columns.
    out_fields = ["status", "message", "group", "year", "authors", "title", "download_url", "target_path", "file_name"]
    with RESULTS.open("w", newline='', encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        for row in rows:
            url = row.get("download_url", "").strip()
            target = ROOT / row.get("target_path", "")
            if not url:
                status, msg = "SKIP", "no direct URL"
            else:
                status, msg = fetch(url, target)
                time.sleep(0.75)
            w.writerow({
                "status": status,
                "message": msg,
                "group": row.get("group", ""),
                "year": row.get("year", ""),
                "authors": row.get("authors", ""),
                "title": row.get("title", ""),
                "download_url": url,
                "target_path": row.get("target_path", ""),
                "file_name": row.get("file_name", ""),
            })
            print(f"[{status}] {row.get('group','?')} - {row.get('title','?')} :: {msg}")
    print(f"\nResults written to {RESULTS}")

if __name__ == "__main__":
    main()
