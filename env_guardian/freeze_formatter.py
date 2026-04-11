"""Format FreezeReport output as text, JSON, or CSV."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.freezer import FreezeReport, FreezeViolation


def _sorted_violations(violations: List[FreezeViolation]) -> List[FreezeViolation]:
    return sorted(violations, key=lambda v: v.key)


def format_text(report: FreezeReport) -> str:
    lines: List[str] = []
    lines.append("=== Freeze Check Report ===")
    lines.append(f"Checksum : {report.checksum}")
    lines.append(f"Keys     : {len(report.frozen_env)}")
    lines.append(f"Status   : {'CLEAN' if report.is_clean() else 'VIOLATIONS FOUND'}")
    lines.append("")

    if report.is_clean():
        lines.append("No violations detected. Frozen env is intact.")
    else:
        lines.append(f"Violations ({report.violation_count()}):")
        for v in _sorted_violations(report.violations):
            lines.append(f"  {v}")

    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: FreezeReport) -> str:
    payload = {
        "checksum": report.checksum,
        "frozen_key_count": len(report.frozen_env),
        "is_clean": report.is_clean(),
        "violation_count": report.violation_count(),
        "violations": [
            {
                "key": v.key,
                "expected": v.expected,
                "actual": v.actual,
                "reason": v.reason,
            }
            for v in _sorted_violations(report.violations)
        ],
        "summary": report.summary(),
    }
    return json.dumps(payload, indent=2)


def format_csv(report: FreezeReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "expected", "actual", "reason"])
    if report.is_clean():
        for key in sorted(report.frozen_env):
            writer.writerow([key, report.frozen_env[key], report.frozen_env[key], "ok"])
    else:
        for v in _sorted_violations(report.violations):
            writer.writerow([v.key, v.expected, v.actual, v.reason])
    return buf.getvalue()
