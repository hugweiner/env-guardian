"""Format a SplitReport as text, JSON, or CSV."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from env_guardian.splitter import SplitEntry, SplitReport


def _sorted_entries(report: SplitReport) -> List[SplitEntry]:
    return sorted(report.all_entries(), key=lambda e: (e.bucket, e.key))


def format_text(report: SplitReport) -> str:
    lines: List[str] = ["Env Split Report", "================"]
    for bucket in sorted(report.bucket_names()):
        entries = sorted(report.by_bucket(bucket), key=lambda e: e.key)
        lines.append(f"\n[{bucket}] ({len(entries)} key(s))")
        for e in entries:
            lines.append(f"  {e.key}={e.value}")
    lines.append(f"\n{report.summary()}")
    return "\n".join(lines)


def format_json(report: SplitReport) -> str:
    data = {
        "buckets": {
            bucket: report.bucket_env(bucket)
            for bucket in sorted(report.bucket_names())
        },
        "summary": report.summary(),
    }
    return json.dumps(data, indent=2)


def format_csv(report: SplitReport) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["bucket", "key", "value"])
    for e in _sorted_entries(report):
        writer.writerow([e.bucket, e.key, e.value])
    return buf.getvalue()
