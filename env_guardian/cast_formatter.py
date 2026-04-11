"""Formatters for CastReport output (text, JSON, CSV)."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.caster import CastEntry, CastReport


def _sorted_entries(report: CastReport) -> List[CastEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: CastReport) -> str:
    lines = ["Cast Report", "==========="]
    if not report.entries:
        lines.append("No entries.")
        return "\n".join(lines)
    for entry in _sorted_entries(report):
        lines.append(f"  {entry}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: CastReport) -> str:
    data = [
        {
            "key": e.key,
            "raw_value": e.raw_value,
            "cast_value": e.cast_value,
            "inferred_type": e.inferred_type,
        }
        for e in _sorted_entries(report)
    ]
    return json.dumps(data, indent=2)


def format_csv(report: CastReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "raw_value", "cast_value", "inferred_type"])
    for e in _sorted_entries(report):
        writer.writerow([e.key, e.raw_value, str(e.cast_value), e.inferred_type])
    return buf.getvalue()
