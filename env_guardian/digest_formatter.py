"""Formatters for DigestReport output."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.digester import DigestEntry, DigestReport


def _sorted_entries(report: DigestReport) -> List[DigestEntry]:
    return sorted(report.entries.values(), key=lambda e: e.key)


def format_text(report: DigestReport) -> str:
    lines: List[str] = [
        f"Digest Report  [{report.algorithm.upper()}]",
        "-" * 50,
    ]
    for entry in _sorted_entries(report):
        lines.append(f"  {entry.key:<30} {entry.checksum}")
    lines.append("-" * 50)
    lines.append(f"  Fingerprint: {report.fingerprint()}")
    lines.append(f"  {report.summary()}")
    return "\n".join(lines)


def format_json(report: DigestReport) -> str:
    payload = {
        "algorithm": report.algorithm,
        "fingerprint": report.fingerprint(),
        "entries": [
            {"key": e.key, "checksum": e.checksum}
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(payload, indent=2)


def format_csv(report: DigestReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "checksum", "algorithm"])
    for entry in _sorted_entries(report):
        writer.writerow([entry.key, entry.checksum, report.algorithm])
    return buf.getvalue()
