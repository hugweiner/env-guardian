"""Formatters for HashReport output."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.hasher import HashEntry, HashReport


def _sorted_entries(report: HashReport) -> List[HashEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: HashReport) -> str:
    lines: List[str] = []
    lines.append(f"Hash Report  ({report.algorithm})")
    lines.append("=" * 50)
    if not report.entries:
        lines.append("  (no entries)")
    else:
        for entry in _sorted_entries(report):
            lines.append(f"  {entry.key:<30} {entry.digest}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: HashReport) -> str:
    payload = {
        "algorithm": report.algorithm,
        "summary": report.summary(),
        "entries": [
            {"key": e.key, "algorithm": e.algorithm, "digest": e.digest}
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(payload, indent=2)


def format_csv(report: HashReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "algorithm", "digest"])
    for entry in _sorted_entries(report):
        writer.writerow([entry.key, entry.algorithm, entry.digest])
    return buf.getvalue()
