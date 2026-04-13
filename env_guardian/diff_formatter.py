"""Formatters for DiffReport (line-level differ output)."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.differ import DiffReport, DiffLine


def _sorted_lines(report: DiffReport) -> List[DiffLine]:
    return sorted(report.lines, key=lambda ln: ln.key)


def format_text(report: DiffReport) -> str:
    lines: List[str] = []
    lines.append("=== Env Diff ===")
    for ln in _sorted_lines(report):
        prefix = {
            "added": "+",
            "removed": "-",
            "changed": "~",
            "unchanged": " ",
        }.get(ln.status, " ")
        if ln.status == "changed":
            lines.append(f"  {prefix} {ln.key}: {ln.old_value!r} -> {ln.new_value!r}")
        elif ln.status == "added":
            lines.append(f"  {prefix} {ln.key}={ln.new_value!r}")
        elif ln.status == "removed":
            lines.append(f"  {prefix} {ln.key}={ln.old_value!r}")
        else:
            lines.append(f"  {prefix} {ln.key}")
    added = len(report.added())
    removed = len(report.removed())
    changed = len(report.changed())
    lines.append(
        f"\nSummary: +{added} added, -{removed} removed, ~{changed} changed"
    )
    return "\n".join(lines)


def format_json(report: DiffReport) -> str:
    payload = [
        {
            "key": ln.key,
            "status": ln.status,
            "old_value": ln.old_value,
            "new_value": ln.new_value,
        }
        for ln in _sorted_lines(report)
    ]
    return json.dumps(payload, indent=2)


def format_csv(report: DiffReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "status", "old_value", "new_value"])
    for ln in _sorted_lines(report):
        writer.writerow([ln.key, ln.status, ln.old_value or "", ln.new_value or ""])
    return buf.getvalue()
