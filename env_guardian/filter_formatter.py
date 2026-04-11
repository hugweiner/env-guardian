"""Format FilterReport as text, JSON, or CSV."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.filterer import FilterEntry, FilterReport


def _sorted_entries(report: FilterReport) -> List[FilterEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: FilterReport) -> str:
    lines: List[str] = ["=== Filter Report ==="]
    entries = _sorted_entries(report)
    if not entries:
        lines.append("No keys matched the filter rules.")
    else:
        for entry in entries:
            lines.append(f"  {entry.key}={entry.value!r}  [{entry.matched_rule}]")
    lines.append("")
    if report.excluded_keys:
        lines.append(f"Excluded ({report.excluded_count()}):")
        for k in sorted(report.excluded_keys):
            lines.append(f"  - {k}")
        lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: FilterReport) -> str:
    data = {
        "matched": [
            {"key": e.key, "value": e.value, "matched_rule": e.matched_rule}
            for e in _sorted_entries(report)
        ],
        "excluded": sorted(report.excluded_keys),
        "summary": report.summary(),
    }
    return json.dumps(data, indent=2)


def format_csv(report: FilterReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "matched_rule"])
    for entry in _sorted_entries(report):
        writer.writerow([entry.key, entry.value, entry.matched_rule])
    return buf.getvalue()
