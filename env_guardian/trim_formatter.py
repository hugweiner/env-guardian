"""Format TrimReport as text, JSON, or CSV."""

import csv
import io
import json
from typing import List

from env_guardian.trimmer import TrimReport, TrimWarning


def _sorted_warnings(warnings: List[TrimWarning]) -> List[TrimWarning]:
    return sorted(warnings, key=lambda w: w.key)


def format_text(report: TrimReport) -> str:
    lines: List[str] = []
    lines.append("=== Trim Report ===")
    if report.is_clean():
        lines.append("No trimming needed. All values are clean.")
    else:
        lines.append(f"Trimmed {report.trimmed_count()} value(s):\n")
        for w in _sorted_warnings(report.warnings):
            lines.append(f"  {w}")
    lines.append(f"\nSummary: {report.summary()}")
    return "\n".join(lines)


def format_json(report: TrimReport) -> str:
    data = {
        "summary": report.summary(),
        "trimmed_count": report.trimmed_count(),
        "warnings": [
            {
                "key": w.key,
                "original": w.original,
                "trimmed": w.trimmed,
                "reason": w.reason,
            }
            for w in _sorted_warnings(report.warnings)
        ],
        "env": report.env,
    }
    return json.dumps(data, indent=2)


def format_csv(report: TrimReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "original", "trimmed", "reason"])
    for w in _sorted_warnings(report.warnings):
        writer.writerow([w.key, w.original, w.trimmed, w.reason])
    return buf.getvalue()
