"""Format InjectReport as text, JSON, or CSV."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.injector import InjectEntry, InjectReport


def _sorted_entries(report: InjectReport) -> List[InjectEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: InjectReport) -> str:
    lines: List[str] = ["=== Inject Report ==="]
    entries = _sorted_entries(report)
    if not entries:
        lines.append("No keys injected.")
    else:
        for entry in entries:
            tag = "[overwrite]" if entry.overwritten else "[new]"
            lines.append(f"  {tag} {entry}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: InjectReport) -> str:
    data = {
        "summary": {
            "injected": report.injected_count,
            "overwritten": report.overwritten_count,
        },
        "entries": [
            {
                "key": e.key,
                "value": e.value,
                "overwritten": e.overwritten,
                "previous_value": e.previous_value,
            }
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: InjectReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "overwritten", "previous_value"])
    for entry in _sorted_entries(report):
        writer.writerow([
            entry.key,
            entry.value,
            str(entry.overwritten),
            entry.previous_value or "",
        ])
    return buf.getvalue()
