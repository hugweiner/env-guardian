"""Format SelectReport for display."""
from __future__ import annotations
import csv
import io
import json
from typing import List

from env_guardian.selector import SelectReport, SelectEntry


def _sorted_entries(report: SelectReport) -> List[SelectEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: SelectReport) -> str:
    lines = ["# env-guardian select", ""]
    if report.selected_count == 0:
        lines.append("No keys selected.")
    else:
        for entry in _sorted_entries(report):
            lines.append(f"  {entry.key:<30} {entry.value!r:<30} [{entry.reason}]")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: SelectReport) -> str:
    data = {
        "summary": report.summary(),
        "selected_count": report.selected_count,
        "entries": [
            {"key": e.key, "value": e.value, "reason": e.reason}
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: SelectReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "reason"])
    for entry in _sorted_entries(report):
        writer.writerow([entry.key, entry.value, entry.reason])
    return buf.getvalue()
