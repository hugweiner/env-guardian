"""Formatters for AliasReport output."""
import csv
import io
import json
from typing import List

from env_guardian.aliaser import AliasEntry, AliasReport


def _sorted_entries(report: AliasReport) -> List[AliasEntry]:
    return sorted(report.entries, key=lambda e: e.original_key)


def format_text(report: AliasReport) -> str:
    lines = ["=== Alias Report ==="]
    for entry in _sorted_entries(report):
        if entry.skipped:
            lines.append(f"  [SKIP] {entry.original_key} -> {entry.alias_key}  ({entry.skip_reason})")
        else:
            lines.append(f"  {entry.original_key} -> {entry.alias_key} = {entry.value}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: AliasReport) -> str:
    data = {
        "summary": report.summary(),
        "aliased_count": report.aliased_count(),
        "skipped_count": report.skipped_count(),
        "entries": [
            {
                "original_key": e.original_key,
                "alias_key": e.alias_key,
                "value": e.value,
                "skipped": e.skipped,
                "skip_reason": e.skip_reason,
            }
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: AliasReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["original_key", "alias_key", "value", "skipped", "skip_reason"])
    for e in _sorted_entries(report):
        writer.writerow([e.original_key, e.alias_key, e.value, e.skipped, e.skip_reason or ""])
    return buf.getvalue()
