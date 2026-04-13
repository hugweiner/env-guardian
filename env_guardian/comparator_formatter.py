"""Formatters for EnvDiff comparison results."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.comparator import EnvDiff


def _sorted_keys(diff: EnvDiff) -> List[str]:
    all_keys = set(diff.missing) | set(diff.extra) | set(diff.mismatched)
    return sorted(all_keys)


def format_text(diff: EnvDiff) -> str:
    lines: List[str] = []
    lines.append("=== Environment Comparison ===")
    if diff.missing:
        lines.append(f"\nMissing keys ({len(diff.missing)}):")
        for key in sorted(diff.missing):
            lines.append(f"  - {key}")
    if diff.extra:
        lines.append(f"\nExtra keys ({len(diff.extra)}):")
        for key in sorted(diff.extra):
            lines.append(f"  + {key}")
    if diff.mismatched:
        lines.append(f"\nMismatched values ({len(diff.mismatched)}):")
        for key in sorted(diff.mismatched):
            lines.append(f"  ~ {key}")
    if not diff.missing and not diff.extra and not diff.mismatched:
        lines.append("No differences found.")
    lines.append(f"\nSummary: {diff.summary()}")
    return "\n".join(lines)


def format_json(diff: EnvDiff) -> str:
    payload = {
        "missing": sorted(diff.missing),
        "extra": sorted(diff.extra),
        "mismatched": sorted(diff.mismatched),
        "is_clean": diff.is_clean(),
        "summary": diff.summary(),
    }
    return json.dumps(payload, indent=2)


def format_csv(diff: EnvDiff) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "issue"])
    for key in sorted(diff.missing):
        writer.writerow([key, "missing"])
    for key in sorted(diff.extra):
        writer.writerow([key, "extra"])
    for key in sorted(diff.mismatched):
        writer.writerow([key, "mismatched"])
    return buf.getvalue()
