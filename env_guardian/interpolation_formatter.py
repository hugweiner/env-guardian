"""Format InterpolationResult for display or export."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.interpolator import InterpolationResult, InterpolationWarning


def _sorted_warnings(warnings: List[InterpolationWarning]) -> List[InterpolationWarning]:
    return sorted(warnings, key=lambda w: (w.key, w.ref))


def format_text(result: InterpolationResult) -> str:
    lines: List[str] = ["=== Interpolation Result ==="]
    if result.is_clean:
        lines.append("No unresolved references found.")
    else:
        lines.append(f"Warnings ({len(result.warnings)}):")
        for w in _sorted_warnings(result.warnings):
            lines.append(f"  WARN  [{w.key}] -> ${w.ref}: {w.message}")
    lines.append("")
    lines.append(f"Resolved keys: {len(result.env)}")
    return "\n".join(lines)


def format_json(result: InterpolationResult) -> str:
    payload = {
        "resolved_env": result.env,
        "warnings": [
            {"key": w.key, "ref": w.ref, "message": w.message}
            for w in _sorted_warnings(result.warnings)
        ],
        "is_clean": result.is_clean,
    }
    return json.dumps(payload, indent=2)


def format_csv(result: InterpolationResult) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "ref", "message"])
    for w in _sorted_warnings(result.warnings):
        writer.writerow([w.key, w.ref, w.message])
    return buf.getvalue()
