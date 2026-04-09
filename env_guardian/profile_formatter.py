"""Formatters for ProfileReport output."""

import csv
import io
import json
from typing import List

from env_guardian.profiler import ProfileEntry, ProfileReport

_CATEGORY_ORDER = ["secret", "url", "flag", "numeric", "general"]


def _sorted_entries(entries: List[ProfileEntry]) -> List[ProfileEntry]:
    return sorted(
        entries,
        key=lambda e: (_CATEGORY_ORDER.index(e.category) if e.category in _CATEGORY_ORDER else 99, e.key),
    )


def format_text(report: ProfileReport) -> str:
    lines = ["=== Environment Profile ===", report.summary(), "", "--- Variables ---"]
    for entry in _sorted_entries(report.entries):
        lines.append(f"  {str(entry)}")
    return "\n".join(lines)


def format_json(report: ProfileReport) -> str:
    data = {
        "total": report.total,
        "empty_count": report.empty_count,
        "categories": {
            cat: [e.key for e in items]
            for cat, items in report.by_category.items()
        },
        "entries": [
            {
                "key": e.key,
                "category": e.category,
                "is_empty": e.is_empty,
                "value_length": e.value_length,
            }
            for e in _sorted_entries(report.entries)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: ProfileReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "category", "is_empty", "value_length"])
    for entry in _sorted_entries(report.entries):
        writer.writerow([entry.key, entry.category, entry.is_empty, entry.value_length])
    return buf.getvalue()
