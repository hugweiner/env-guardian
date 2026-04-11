"""Format a SplitReport as text, JSON, or CSV."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.splitter import SplitEntry, SplitReport


def _sorted_entries(report: SplitReport) -> List[SplitEntry]:
    return sorted(report.entries, key=lambda e: (e.bucket, e.key))


def format_text(report: SplitReport) -> str:
    lines: List[str] = ["ENV SPLIT REPORT", "=" * 40]
    for bucket in report.bucket_names():
        lines.append(f"\n[{bucket}]")
        bucket_env = report.get_bucket(bucket)
        for key in sorted(bucket_env):
            lines.append(f"  {key}={bucket_env[key]}")
    lines.append("")
    lines.append(report.summary())
    return "\n".join(lines)


def format_json(report: SplitReport) -> str:
    payload = {
        "summary": report.summary(),
        "bucket_count": report.bucket_count(),
        "buckets": {
            bucket: report.get_bucket(bucket) for bucket in report.bucket_names()
        },
    }
    return json.dumps(payload, indent=2)


def format_csv(report: SplitReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["bucket", "key", "value"])
    for entry in _sorted_entries(report):
        writer.writerow([entry.bucket, entry.key, entry.value])
    return buf.getvalue()
