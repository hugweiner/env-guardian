"""Formatters for ArchiveStore output."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.archiver import ArchiveEntry, ArchiveStore


def _sorted_entries(store: ArchiveStore) -> List[ArchiveEntry]:
    return sorted(store.entries, key=lambda e: e.timestamp)


def format_text(store: ArchiveStore) -> str:
    lines: List[str] = ["=== Archive ==="]
    entries = _sorted_entries(store)
    if not entries:
        lines.append("  (empty)")
    else:
        for e in entries:
            lines.append(f"  [{e.timestamp}] {e.label} — {len(e.env)} key(s)")
    lines.append("")
    lines.append(store.summary())
    return "\n".join(lines)


def format_json(store: ArchiveStore) -> str:
    payload = [
        {"label": e.label, "timestamp": e.timestamp, "env": e.env}
        for e in _sorted_entries(store)
    ]
    return json.dumps({"archive": payload, "count": store.count}, indent=2)


def format_csv(store: ArchiveStore) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["timestamp", "label", "key", "value"])
    for e in _sorted_entries(store):
        for k, v in sorted(e.env.items()):
            writer.writerow([e.timestamp, e.label, k, v])
    return buf.getvalue()
