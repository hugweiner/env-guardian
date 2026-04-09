"""Formatters for DiffReport output (text, json, csv)."""

import csv
import io
import json
from typing import List

from env_guardian.differ import DiffLine, DiffReport

_STATUS_ORDER = {"removed": 0, "changed": 1, "added": 2, "unchanged": 3}


def _sorted_lines(report: DiffReport) -> List[DiffLine]:
    return sorted(report.lines, key=lambda l: (_STATUS_ORDER.get(l.status, 99), l.key))


def format_text(report: DiffReport, show_unchanged: bool = False) -> str:
    lines = ["Diff Report", "=" * 40]
    if report.is_clean():
        lines.append("No differences found.")
    else:
        for line in _sorted_lines(report):
            if line.status == "unchanged" and not show_unchanged:
                continue
            lines.append(str(line))
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: DiffReport) -> str:
    data = [
        {
            "key": l.key,
            "status": l.status,
            "source_value": l.source_value,
            "target_value": l.target_value,
        }
        for l in _sorted_lines(report)
    ]
    return json.dumps({"summary": report.summary(), "diff": data}, indent=2)


def format_csv(report: DiffReport) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=["key", "status", "source_value", "target_value"]
    )
    writer.writeheader()
    for line in _sorted_lines(report):
        writer.writerow(
            {
                "key": line.key,
                "status": line.status,
                "source_value": line.source_value if line.source_value is not None else "",
                "target_value": line.target_value if line.target_value is not None else "",
            }
        )
    return buf.getvalue()
