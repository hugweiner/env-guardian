"""Classify environment variables into named groups based on key patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


_RULES: List[tuple[str, str]] = [
    (r"(?i)(secret|token|password|passwd|pwd|api_key|private)", "secret"),
    (r"(?i)(url|uri|host|endpoint|domain|port)", "network"),
    (r"(?i)(db|database|mongo|postgres|mysql|redis|sqlite)", "database"),
    (r"(?i)(log|debug|verbose|trace)", "logging"),
    (r"(?i)(env|environment|stage|region|zone|namespace)", "deployment"),
    (r"(?i)(timeout|retry|limit|max|min|threshold)", "tuning"),
    (r"(?i)(feature|flag|enable|disable|toggle)", "feature_flag"),
]


@dataclass
class ClassifyEntry:
    key: str
    value: str
    group: str

    def __str__(self) -> str:
        return f"{self.group:<16} {self.key}={self.value}"


@dataclass
class ClassifyReport:
    entries: List[ClassifyEntry] = field(default_factory=list)

    def by_group(self) -> Dict[str, List[ClassifyEntry]]:
        groups: Dict[str, List[ClassifyEntry]] = {}
        for entry in self.entries:
            groups.setdefault(entry.group, []).append(entry)
        return groups

    def group_names(self) -> List[str]:
        return sorted(self.by_group().keys())

    def count_by_group(self) -> Dict[str, int]:
        return {g: len(v) for g, v in self.by_group().items()}

    def summary(self) -> str:
        counts = self.count_by_group()
        parts = [f"{g}:{n}" for g, n in sorted(counts.items())]
        return "groups=" + ", ".join(parts) if parts else "no entries"


def _classify_key(key: str) -> str:
    for pattern, group in _RULES:
        if re.search(pattern, key):
            return group
    return "general"


def classify_env(env: Dict[str, str]) -> ClassifyReport:
    """Classify each key in *env* into a named group."""
    report = ClassifyReport()
    for key, value in env.items():
        group = _classify_key(key)
        report.entries.append(ClassifyEntry(key=key, value=value, group=group))
    return report
