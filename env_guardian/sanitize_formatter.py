"""Format :class:`SanitizeReport` as text, JSON, or CSV."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.sanitizer import SanitizeReport, SanitizeWarning


def _sorted_warnings(report: SanitizeReport) -> List[SanitizeWarning]:
    return sorted(report.warnings, key=lambda w: w.key)


def format_text(report: SanitizeReport) -> str:
    lines: List[str] = ["=== Sanitize Report ==="]
    if report.is_clean():
        lines.append("No issues found — all values are clean.")
        return "\n".join(lines)

    lines.append(f"Sanitized: {len(report.warnings)} value(s)\n")
    for w in _sorted_warnings(report):
        lines.append(f"  {w.key}")
        lines.append(f"    reason   : {w.reason}")
        lines.append(f"    original : {w.original!r}")
        lines.append(f"    sanitized: {w.sanitized!r}")
    lines.append(f"\n{report.summary()}")
    return "\n".join(lines)


def format_json(report: SanitizeReport) -> str:
    data = {
        "summary": report.summary(),
        "clean": report.is_clean(),
        "warnings": [
            {
                "key": w.key,
                "reason": w.reason,
                "original": w.original,
                "sanitized": w.sanitized,
            }
            for w in _sorted_warnings(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: SanitizeReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "reason", "original", "sanitized"])
    for w in _sorted_warnings(report):
        writer.writerow([w.key, w.reason, w.original, w.sanitized])
    return buf.getvalue()
