"""Formatters for DeprecateReport — text, JSON, and CSV output."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.deprecator import DeprecateReport, DeprecationWarning_


def _sorted_warnings(report: DeprecateReport) -> List[DeprecationWarning_]:
    return sorted(report.warnings, key=lambda w: w.key)


def format_text(report: DeprecateReport) -> str:
    lines: List[str] = ["=== Deprecation Report ==="]
    if report.is_clean():
        lines.append("No deprecated keys found.")
    else:
        for w in _sorted_warnings(report):
            replacement = f" -> {w.replacement}" if w.replacement else ""
            lines.append(f"  [DEPRECATED] {w.key}{replacement}: {w.reason}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: DeprecateReport) -> str:
    data = {
        "summary": report.summary(),
        "is_clean": report.is_clean(),
        "deprecated_keys": [
            {
                "key": w.key,
                "reason": w.reason,
                "replacement": w.replacement,
            }
            for w in _sorted_warnings(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: DeprecateReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "reason", "replacement"])
    for w in _sorted_warnings(report):
        writer.writerow([w.key, w.reason, w.replacement or ""])
    return buf.getvalue()
