"""Format AuditReport output for CLI display and export."""

import json
import csv
import io
from typing import Dict, Any

from env_guardian.auditor import AuditReport

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _sorted_issues(report: AuditReport):
    return sorted(report.issues, key=lambda i: SEVERITY_ORDER.get(i.severity, 99))


def format_text(report: AuditReport) -> str:
    """Return a human-readable text summary of the audit report."""
    if report.is_clean():
        return "Audit passed: no issues found.\n"

    lines = [f"Audit Report — {report.summary()}", ""]
    for issue in _sorted_issues(report):
        lines.append(f"  {issue}")
    lines.append("")
    return "\n".join(lines)


def format_json(report: AuditReport) -> str:
    """Serialize the audit report to a JSON string."""
    data: Dict[str, Any] = {
        "clean": report.is_clean(),
        "summary": report.summary(),
        "issues": [
            {"key": i.key, "severity": i.severity, "message": i.message}
            for i in _sorted_issues(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: AuditReport) -> str:
    """Serialize the audit report to a CSV string."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["key", "severity", "message"])
    writer.writeheader()
    for issue in _sorted_issues(report):
        writer.writerow({"key": issue.key, "severity": issue.severity, "message": issue.message})
    return output.getvalue()
