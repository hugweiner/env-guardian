"""Format AnnotateReport as text, JSON, or CSV."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.annotator import AnnotateReport, AnnotationEntry


def _sorted_entries(report: AnnotateReport) -> List[AnnotationEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: AnnotateReport) -> str:
    lines: List[str] = ["=== Annotation Report ==="]
    entries = _sorted_entries(report)
    if not entries:
        lines.append("No keys found.")
        return "\n".join(lines)

    for entry in entries:
        annotation_str = entry.annotation if entry.annotation else "(no annotation)"
        lines.append(f"  {entry.key}")
        lines.append(f"    value      : {entry.value}")
        lines.append(f"    annotation : {annotation_str}")

    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: AnnotateReport) -> str:
    data = [
        {
            "key": e.key,
            "value": e.value,
            "annotation": e.annotation,
        }
        for e in _sorted_entries(report)
    ]
    return json.dumps(
        {"summary": report.summary(), "entries": data},
        indent=2,
    )


def format_csv(report: AnnotateReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "annotation"])
    for entry in _sorted_entries(report):
        writer.writerow([entry.key, entry.value, entry.annotation or ""])
    return buf.getvalue()
