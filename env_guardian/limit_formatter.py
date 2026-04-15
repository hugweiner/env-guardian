"""Formatters for LimitReport output."""
from __future__ import annotations
import csv
import io
import json
from typing import List

from env_guardian.limiter import LimitReport, LimitViolation


def _sorted_violations(report: LimitReport) -> List[LimitViolation]:
    return sorted(report.violations, key=lambda v: v.key)


def format_text(report: LimitReport) -> str:
    lines = ["=== Limit Report ==="]
    if report.is_clean():
        lines.append("No violations found.")
    else:
        lines.append(f"Violations: {report.violation_count()}")
        for v in _sorted_violations(report):
            lines.append(f"  [{v.kind.upper()}] {v}")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: LimitReport) -> str:
    data = {
        "clean": report.is_clean(),
        "violation_count": report.violation_count(),
        "violations": [
            {
                "key": v.key,
                "kind": v.kind,
                "actual_length": v.actual_length,
                "min_length": v.min_length,
                "max_length": v.max_length,
                "value": v.value,
            }
            for v in _sorted_violations(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: LimitReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "kind", "actual_length", "min_length", "max_length", "value"])
    for v in _sorted_violations(report):
        writer.writerow(
            [v.key, v.kind, v.actual_length, v.min_length, v.max_length, v.value]
        )
    return buf.getvalue()
