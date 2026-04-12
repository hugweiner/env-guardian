"""Formatters for CompactReport output."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.compactor import CompactReport, CompactWarning


def _sorted_warnings(report: CompactReport) -> List[CompactWarning]:
    return sorted(report.warnings, key=lambda w: w.key)


def format_text(report: CompactReport) -> str:
    lines: List[str] = ["=== Compact Report ==="]
    if report.is_clean():
        lines.append("No empty values found. Nothing removed.")
    else:
        lines.append(f"Removed {report.removed_count()} key(s) with empty/blank values:")
        for w in _sorted_warnings(report):
            display = repr(w.original_value) if w.original_value != "" else "(empty string)"
            lines.append(f"  - {w.key}: {display}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: CompactReport) -> str:
    payload = {
        "summary": report.summary(),
        "removed_count": report.removed_count(),
        "removed": [
            {"key": w.key, "original_value": w.original_value}
            for w in _sorted_warnings(report)
        ],
        "compacted_env": dict(sorted(report.compacted_env.items())),
    }
    return json.dumps(payload, indent=2)


def format_csv(report: CompactReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", "original_value"])
    for w in _sorted_warnings(report):
        writer.writerow([w.key, "removed", w.original_value])
    for key, value in sorted(report.compacted_env.items()):
        writer.writerow([key, "retained", value])
    return buf.getvalue()
