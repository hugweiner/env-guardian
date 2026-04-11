"""Formatters for RotateReport output."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.rotator import RotateEntry, RotateReport


def _sorted_entries(report: RotateReport) -> List[RotateEntry]:
    return sorted(report.entries, key=lambda e: (not e.stale, e.key))


def format_text(report: RotateReport) -> str:
    lines: List[str] = ["=== Key Rotation Report ==="]
    if report.is_clean():
        lines.append("No stale keys detected.")
    else:
        lines.append(f"Stale keys: {report.stale_count}")
    lines.append("")
    for entry in _sorted_entries(report):
        tag = "[STALE]" if entry.stale else "[ok]  "
        lines.append(f"  {tag} {entry.key} -> {entry.rotated_key}")
        lines.append(f"         reason : {entry.reason}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: RotateReport) -> str:
    data = {
        "summary": report.summary(),
        "stale_count": report.stale_count,
        "entries": [
            {
                "key": e.key,
                "rotated_key": e.rotated_key,
                "stale": e.stale,
                "reason": e.reason,
            }
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: RotateReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "rotated_key", "stale", "reason"])
    for e in _sorted_entries(report):
        writer.writerow([e.key, e.rotated_key, e.stale, e.reason])
    return buf.getvalue()
