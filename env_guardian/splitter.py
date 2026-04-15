"""Split an env dict into named buckets based on key-prefix rules."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SplitEntry:
    key: str
    value: str
    bucket: str

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.bucket}: {self.key}={self.value}"


@dataclass
class SplitReport:
    _entries: List[SplitEntry] = field(default_factory=list)

    def add(self, entry: SplitEntry) -> None:
        self._entries.append(entry)

    def bucket_names(self) -> List[str]:
        seen: List[str] = []
        for e in self._entries:
            if e.bucket not in seen:
                seen.append(e.bucket)
        return seen

    def by_bucket(self, name: str) -> List[SplitEntry]:
        return [e for e in self._entries if e.bucket == name]

    def all_entries(self) -> List[SplitEntry]:
        return list(self._entries)

    def bucket_env(self, name: str) -> Dict[str, str]:
        return {e.key: e.value for e in self.by_bucket(name)}

    def summary(self) -> str:
        buckets = self.bucket_names()
        parts = ", ".join(f"{b}={len(self.by_bucket(b))}" for b in buckets)
        return f"{len(self._entries)} keys split into {len(buckets)} bucket(s): {parts}"


_UNGROUPED = "ungrouped"


def split_env(
    env: Dict[str, str],
    rules: Optional[Dict[str, str]] = None,
) -> SplitReport:
    """Split *env* into buckets.

    *rules* maps a bucket name to a key prefix, e.g.
        {"db": "DB_", "redis": "REDIS_"}
    Keys that match no rule land in the ``ungrouped`` bucket.
    """
    rules = rules or {}
    report = SplitReport()
    for key, value in env.items():
        matched: Optional[str] = None
        for bucket, prefix in rules.items():
            if key.startswith(prefix):
                matched = bucket
                break
        report.add(SplitEntry(key=key, value=value, bucket=matched or _UNGROUPED))
    return report
