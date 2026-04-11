"""Format a SampleReport as text, JSON, or CSV."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.sampler import SampleEntry, SampleReport


def _sorted_entries(report: SampleReport) -> List[SampleEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: SampleReport) -> str:
    lines: List[str] = []
    lines.append("=== Env Sample ===")
    lines.append(report.summary())
    lines.append("")

    if not report.entries:
        lines.append("(no keys sampled)")
        return "\n".join(lines)

    lines.append(f"  {'KEY':<40} VALUE")
    lines.append("  " + "-" * 60)
    for entry in _sorted_entries(report):
        truncated = entry.value[:40] + "..." if len(entry.value) > 40 else entry.value
        lines.append(f"  {entry.key:<40} {truncated}")

    return "\n".join(lines)


def format_json(report: SampleReport) -> str:
    data = {
        "strategy": report.strategy,
        "total_keys": report.total_keys,
        "sampled_count": report.sampled_count(),
        "entries": [
            {"key": e.key, "value": e.value, "index": e.index}
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: SampleReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "index"])
    for entry in _sorted_entries(report):
        writer.writerow([entry.key, entry.value, entry.index])
    return buf.getvalue()
