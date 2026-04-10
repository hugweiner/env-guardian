"""Formatters for ScanReport output: text, JSON, CSV."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.scanner import ScanHit, ScanReport

_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def _sorted_hits(hits: List[ScanHit]) -> List[ScanHit]:
    return sorted(hits, key=lambda h: (_SEVERITY_ORDER.get(h.severity, 9), h.key))


def format_text(report: ScanReport) -> str:
    lines: List[str] = ["=== Env Guardian — Scan Report ==="]
    if report.is_clean:
        lines.append("✔ No suspicious values detected.")
    else:
        for hit in _sorted_hits(report.hits):
            masked = hit.value[:4] + "****" if len(hit.value) > 4 else "****"
            lines.append(f"  [{hit.severity.upper():6s}] {hit.key} = {masked}")
            lines.append(f"           {hit.reason}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: ScanReport) -> str:
    data = {
        "clean": report.is_clean,
        "summary": report.summary(),
        "hits": [
            {
                "key": h.key,
                "severity": h.severity,
                "reason": h.reason,
            }
            for h in _sorted_hits(report.hits)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: ScanReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "severity", "reason"])
    for hit in _sorted_hits(report.hits):
        writer.writerow([hit.key, hit.severity, hit.reason])
    return buf.getvalue()
