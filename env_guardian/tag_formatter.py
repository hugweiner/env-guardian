"""Formatters for TagReport output."""

import csv
import io
import json
from typing import List

from env_guardian.tagger import TagEntry, TagReport


def _sorted_entries(entries: List[TagEntry]) -> List[TagEntry]:
    return sorted(entries, key=lambda e: e.key)


def format_text(report: TagReport) -> str:
    lines = ["ENV TAG REPORT", "=" * 40]
    if not report.entries:
        lines.append("No entries found.")
    else:
        for entry in _sorted_entries(report.entries):
            tag_str = ", ".join(entry.tags) if entry.tags else "(untagged)"
            lines.append(f"  {entry.key:<30} [{tag_str}]")
    lines.append("")
    lines.append(f"Summary: {report.summary()}")
    tag_names = report.tag_names()
    if tag_names:
        lines.append("Tags used: " + ", ".join(tag_names))
    return "\n".join(lines)


def format_json(report: TagReport) -> str:
    data = {
        "summary": report.summary(),
        "tags": report.tag_names(),
        "entries": [
            {"key": e.key, "value": e.value, "tags": e.tags}
            for e in _sorted_entries(report.entries)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: TagReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "tags"])
    for entry in _sorted_entries(report.entries):
        writer.writerow([entry.key, entry.value, "|".join(entry.tags)])
    return buf.getvalue()
