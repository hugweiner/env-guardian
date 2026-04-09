"""Format ResolveReport as text, JSON, or CSV."""
import csv
import io
import json
from typing import List

from env_guardian.resolver import ResolveEntry, ResolveReport


def _sorted_entries(report: ResolveReport) -> List[ResolveEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: ResolveReport) -> str:
    lines = ["Resolved Environment Variables", "=" * 34]
    for entry in _sorted_entries(report):
        tag = " [overridden]" if entry.overridden_by else ""
        lines.append(f"  {entry.key}={entry.value}  (source: {entry.source}){tag}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: ResolveReport) -> str:
    data = {
        "layers": report.layers,
        "summary": report.summary(),
        "entries": [
            {
                "key": e.key,
                "value": e.value,
                "source": e.source,
                "overridden": e.overridden_by is not None,
            }
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: ResolveReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "source", "overridden"])
    for e in _sorted_entries(report):
        writer.writerow([e.key, e.value, e.source, str(e.overridden_by is not None)])
    return buf.getvalue()
