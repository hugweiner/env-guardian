"""Format a CloneReport as text, JSON, or CSV."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.cloner import CloneReport, CloneWarning


def _sorted_warnings(warnings: List[CloneWarning]) -> List[CloneWarning]:
    return sorted(warnings, key=lambda w: w.key)


def format_text(report: CloneReport) -> str:
    lines: List[str] = ["=== Clone Report ==="]
    lines.append(report.summary())

    if report.is_clean():
        lines.append("No warnings.")
    else:
        lines.append("")
        lines.append("Warnings:")
        for w in _sorted_warnings(report.warnings):
            lines.append(f"  {w}")

    lines.append("")
    lines.append("Cloned keys:")
    for k, v in sorted(report.cloned_env.items()):
        lines.append(f"  {k}={v}")

    return "\n".join(lines)


def format_json(report: CloneReport) -> str:
    payload = {
        "summary": report.summary(),
        "is_clean": report.is_clean(),
        "warnings": [
            {"key": w.key, "reason": w.reason}
            for w in _sorted_warnings(report.warnings)
        ],
        "cloned_env": dict(sorted(report.cloned_env.items())),
    }
    return json.dumps(payload, indent=2)


def format_csv(report: CloneReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "warning"])

    warning_map = {w.key: w.reason for w in report.warnings}

    for k, v in sorted(report.cloned_env.items()):
        writer.writerow([k, v, warning_map.get(k, "")])

    return buf.getvalue()
