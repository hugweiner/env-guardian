"""Formatters for PadReport output."""

import csv
import io
import json
from typing import List

from env_guardian.padder import PadReport, PadWarning


def _sorted_warnings(warnings: List[PadWarning]) -> List[PadWarning]:
    return sorted(warnings, key=lambda w: w.key)


def format_text(report: PadReport) -> str:
    lines = ["=== Pad Report ==="]
    if report.is_clean():
        lines.append("No padding applied. All values meet the minimum length.")
    else:
        lines.append(f"Padded: {report.padded_count()} value(s)")
        lines.append("")
        for w in _sorted_warnings(report.warnings):
            lines.append(f"  {w}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: PadReport) -> str:
    data = {
        "summary": report.summary(),
        "padded_count": report.padded_count(),
        "warnings": [
            {
                "key": w.key,
                "original": w.original,
                "padded": w.padded,
                "reason": w.reason,
            }
            for w in _sorted_warnings(report.warnings)
        ],
        "env": report.env,
    }
    return json.dumps(data, indent=2)


def format_csv(report: PadReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "original", "padded", "reason"])
    for w in _sorted_warnings(report.warnings):
        writer.writerow([w.key, w.original, w.padded, w.reason])
    return buf.getvalue()
