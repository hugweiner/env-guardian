"""Format MapReport as text, JSON, or CSV."""

import csv
import io
import json
from typing import List

from env_guardian.mapper import MapReport, MapEntry


def _sorted_entries(report: MapReport) -> List[MapEntry]:
    return sorted(report.entries, key=lambda e: e.source_key)


def format_text(report: MapReport) -> str:
    lines = ["Key Mapping Report", "=================="]
    for entry in _sorted_entries(report):
        lines.append(str(entry))
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: MapReport) -> str:
    data = {
        "summary": {
            "mapped": report.mapped_count(),
            "skipped": report.skipped_count(),
        },
        "entries": [
            {
                "source_key": e.source_key,
                "target_key": e.target_key,
                "value": e.value if not e.skipped else None,
                "skipped": e.skipped,
                "skip_reason": e.skip_reason,
            }
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: MapReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["source_key", "target_key", "value", "skipped", "skip_reason"])
    for e in _sorted_entries(report):
        writer.writerow([
            e.source_key,
            e.target_key,
            e.value if not e.skipped else "",
            e.skipped,
            e.skip_reason or "",
        ])
    return buf.getvalue()
