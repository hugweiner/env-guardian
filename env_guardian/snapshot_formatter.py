"""Format SnapshotDiff for text, JSON, and CSV output."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.snapshotter import SnapshotDiff


def format_text(diff: SnapshotDiff, old_label: str = "old", new_label: str = "new") -> str:
    lines: List[str] = []
    lines.append(f"Snapshot diff: {old_label!r} -> {new_label!r}")
    lines.append(f"Summary: {diff.summary()}")
    lines.append("")

    if diff.added:
        lines.append("[ADDED]")
        for key, val in sorted(diff.added.items()):
            lines.append(f"  + {key}={val!r}")

    if diff.removed:
        lines.append("[REMOVED]")
        for key, val in sorted(diff.removed.items()):
            lines.append(f"  - {key}={val!r}")

    if diff.changed:
        lines.append("[CHANGED]")
        for key, (old_val, new_val) in sorted(diff.changed.items()):
            lines.append(f"  ~ {key}: {old_val!r} -> {new_val!r}")

    if diff.is_clean():
        lines.append("  (no differences)")

    return "\n".join(lines)


def format_json(diff: SnapshotDiff) -> str:
    data = {
        "summary": diff.summary(),
        "added": diff.added,
        "removed": diff.removed,
        "changed": {
            key: {"old": old, "new": new}
            for key, (old, new) in diff.changed.items()
        },
    }
    return json.dumps(data, indent=2)


def format_csv(diff: SnapshotDiff) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["change_type", "key", "old_value", "new_value"])

    for key, val in sorted(diff.added.items()):
        writer.writerow(["added", key, "", val])
    for key, val in sorted(diff.removed.items()):
        writer.writerow(["removed", key, val, ""])
    for key, (old_val, new_val) in sorted(diff.changed.items()):
        writer.writerow(["changed", key, old_val, new_val])

    return buf.getvalue()
