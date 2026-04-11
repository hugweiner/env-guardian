"""Format a GroupReport as text, JSON, or CSV."""
import csv
import io
import json
from typing import List

from env_guardian.grouper import GroupEntry, GroupReport


def _sorted_entries(report: GroupReport) -> List[GroupEntry]:
    all_entries: List[GroupEntry] = []
    for name in report.group_names():
        all_entries.extend(sorted(report.by_group(name), key=lambda e: e.key))
    all_entries.extend(sorted(report.ungrouped, key=lambda e: e.key))
    return all_entries


def format_text(report: GroupReport) -> str:
    lines: List[str] = ["ENV VARIABLE GROUPS", "=" * 40]

    for group in report.group_names():
        lines.append(f"[{group}]")
        for entry in sorted(report.by_group(group), key=lambda e: e.key):
            lines.append(f"  {entry.key} = {entry.value}")

    if report.ungrouped:
        lines.append("[ungrouped]")
        for entry in sorted(report.ungrouped, key=lambda e: e.key):
            lines.append(f"  {entry.key} = {entry.value}")

    lines.append("-" * 40)
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: GroupReport) -> str:
    data = {
        "summary": report.summary(),
        "groups": {
            name: [
                {"key": e.key, "value": e.value, "suffix": e.suffix}
                for e in sorted(report.by_group(name), key=lambda e: e.key)
            ]
            for name in report.group_names()
        },
        "ungrouped": [
            {"key": e.key, "value": e.value}
            for e in sorted(report.ungrouped, key=lambda e: e.key)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: GroupReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "group", "suffix"])
    for entry in _sorted_entries(report):
        writer.writerow([entry.key, entry.value, entry.prefix or "(ungrouped)", entry.suffix])
    return buf.getvalue()
