"""Formatters for VersionReport and SchemaDrift output."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.versioner import SchemaDrift, VersionEntry, VersionReport


def _sorted_entries(report: VersionReport) -> List[VersionEntry]:
    return sorted(report.entries, key=lambda e: e.version)


def format_text(report: VersionReport, drift: SchemaDrift | None = None) -> str:
    lines: List[str] = ["=== Version History ==="]
    for entry in _sorted_entries(report):
        lines.append(f"  {entry}")
        lines.append(f"    schema_hash={entry.schema_hash}")
    lines.append("")
    lines.append(f"Total versions: {report.version_count()}")
    if drift is not None:
        lines.append("")
        lines.append("=== Schema Drift ===")
        lines.append(f"  {drift.summary()}")
        if drift.added:
            lines.append("  Added keys:   " + ", ".join(drift.added))
        if drift.removed:
            lines.append("  Removed keys: " + ", ".join(drift.removed))
    return "\n".join(lines)


def format_json(
    report: VersionReport, drift: SchemaDrift | None = None
) -> str:
    data: dict = {
        "versions": [
            {
                "version": e.version,
                "label": e.label,
                "timestamp": e.timestamp,
                "keys": e.keys,
                "schema_hash": e.schema_hash,
            }
            for e in _sorted_entries(report)
        ]
    }
    if drift is not None:
        data["drift"] = {
            "has_drift": drift.has_drift,
            "added": drift.added,
            "removed": drift.removed,
            "summary": drift.summary(),
        }
    return json.dumps(data, indent=2)


def format_csv(report: VersionReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["version", "label", "timestamp", "key_count", "schema_hash"])
    for e in _sorted_entries(report):
        writer.writerow([e.version, e.label, e.timestamp, len(e.keys), e.schema_hash])
    return buf.getvalue()
