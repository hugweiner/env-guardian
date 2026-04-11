"""Formatters for WhitelistReport output."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.whitelister import WhitelistEntry, WhitelistReport


def _sorted_entries(report: WhitelistReport) -> List[WhitelistEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: WhitelistReport) -> str:
    lines: List[str] = ["=== Whitelist Report ==="]
    lines.append(f"Summary: {report.summary()}")
    lines.append("")

    if not report.entries:
        lines.append("No entries.")
        return "\n".join(lines)

    for entry in _sorted_entries(report):
        status = "✓" if entry.allowed else "✗"
        reason = f"  ({entry.reason})" if entry.reason else ""
        lines.append(f"  {status} {entry.key}{reason}")

    return "\n".join(lines)


def format_json(report: WhitelistReport) -> str:
    data = {
        "summary": {
            "allowed": report.allowed_count,
            "blocked": report.blocked_count,
            "total": len(report.entries),
        },
        "entries": [
            {
                "key": e.key,
                "value": e.value,
                "allowed": e.allowed,
                "reason": e.reason,
            }
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: WhitelistReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "value", "allowed", "reason"])
    for entry in _sorted_entries(report):
        writer.writerow([entry.key, entry.value, entry.allowed, entry.reason or ""])
    return buf.getvalue()
