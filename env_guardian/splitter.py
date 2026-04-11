"""Split a flat env dict into multiple named buckets by prefix or pattern."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitEntry:
    key: str
    value: str
    bucket: str

    def __str__(self) -> str:  # pragma: no cover
        return f"[{self.bucket}] {self.key}={self.value}"


@dataclass
class SplitReport:
    entries: List[SplitEntry] = field(default_factory=list)
    _buckets: Dict[str, Dict[str, str]] = field(default_factory=dict, repr=False)

    def add(self, key: str, value: str, bucket: str) -> None:
        self.entries.append(SplitEntry(key=key, value=value, bucket=bucket))
        self._buckets.setdefault(bucket, {})[key] = value

    def bucket_names(self) -> List[str]:
        return sorted(self._buckets.keys())

    def get_bucket(self, name: str) -> Dict[str, str]:
        return dict(self._buckets.get(name, {}))

    def bucket_count(self) -> int:
        return len(self._buckets)

    def summary(self) -> str:
        total = len(self.entries)
        buckets = self.bucket_count()
        return f"{total} key(s) split into {buckets} bucket(s)"


_UNGROUPED = "ungrouped"


def split_env(
    env: Dict[str, str],
    prefixes: Optional[List[str]] = None,
    separator: str = "_",
    include_ungrouped: bool = True,
) -> SplitReport:
    """Split *env* into buckets derived from *prefixes*.

    Each key whose name starts with ``<prefix><separator>`` is placed into the
    bucket named after that prefix (lowercased).  Keys that match no prefix go
    into the ``ungrouped`` bucket when *include_ungrouped* is ``True``.
    """
    report = SplitReport()
    prefixes = [p.upper() for p in (prefixes or [])]

    for key, value in env.items():
        matched_bucket: Optional[str] = None
        for prefix in prefixes:
            if key.upper().startswith(prefix + separator):
                matched_bucket = prefix.lower()
                break

        if matched_bucket is None:
            if include_ungrouped:
                matched_bucket = _UNGROUPED
            else:
                continue

        report.add(key, value, matched_bucket)

    return report
