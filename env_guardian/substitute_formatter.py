"""Formatters for SubstituteReport output."""

import csv
import io
import json
from typing import List

from env_guardian.substitutor import SubstituteReport, SubstituteWarning


def _sorted_warnings(report: SubstituteReport) -> List[SubstituteWarning]:
    return sorted(report.warnings, key=lambda w: (w.key, w.placeholder))


def format_text(report: SubstituteReport) -> str:
    lines: List[str] = ["=== Substitute Report ==="]
    lines.append(report.summary())

    if not report.is_clean():
        lines.append("")
        lines.append("Unresolved placeholders:")
        for w in _sorted_warnings(report):
            lines.append(f"  {w}")

    lines.append("")
    lines.append(f"Resulting env ({len(report.env)} key(s)):")
    for k, v in sorted(report.env.items()):
        lines.append(f"  {k}={v}")

    return "\n".join(lines)


def format_json(report: SubstituteReport) -> str:
    payload = {
        "summary": report.summary(),
        "is_clean": report.is_clean(),
        "unresolved_count": len(report.warnings),
        "warnings": [
            {"key": w.key, "placeholder": w.placeholder, "reason": w.reason}
            for w in _sorted_warnings(report)
        ],
        "env": dict(sorted(report.env.items())),
    }
    return json.dumps(payload, indent=2)


def format_csv(report: SubstituteReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "placeholder", "reason"])
    for w in _sorted_warnings(report):
        writer.writerow([w.key, w.placeholder, w.reason])
    return buf.getvalue()
