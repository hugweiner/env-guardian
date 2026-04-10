"""Format a RenameReport as text, JSON, or CSV."""

import csv
import io
import json
from typing import List

from env_guardian.renamer import RenameEntry, RenameReport


def _sorted_entries(report: RenameReport) -> List[RenameEntry]:
    return sorted(report.entries, key=lambda e: e.old_key)


def format_text(report: RenameReport) -> str:
    lines: List[str] = ["Rename Report", "=" * 40]

    if report.is_clean():
        lines.append("No keys renamed.")
    else:
        for entry in _sorted_entries(report):
            lines.append(str(entry))

    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: RenameReport) -> str:
    data = {
        "summary": {
            "renamed": report.renamed_count(),
            "skipped": report.skipped_count(),
        },
        "entries": [
            {
                "old_key": e.old_key,
                "new_key": e.new_key,
                "value": e.value,
                "skipped": e.skipped,
                "skip_reason": e.skip_reason,
            }
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: RenameReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["old_key", "new_key", "value", "skipped", "skip_reason"])
    for e in _sorted_entries(report):
        writer.writerow([e.old_key, e.new_key, e.value, e.skipped, e.skip_reason or ""])
    return buf.getvalue()
