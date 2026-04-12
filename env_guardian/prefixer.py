"""Prefixer: add or strip a prefix from environment variable keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PrefixEntry:
    original_key: str
    new_key: str
    value: str
    action: str  # 'added' | 'stripped' | 'unchanged'

    def __str__(self) -> str:
        return f"{self.original_key} -> {self.new_key} [{self.action}]"


@dataclass
class PrefixReport:
    entries: List[PrefixEntry] = field(default_factory=list)

    def add(self, entry: PrefixEntry) -> None:
        self.entries.append(entry)

    @property
    def modified_count(self) -> int:
        return sum(1 for e in self.entries if e.action != "unchanged")

    @property
    def result_env(self) -> Dict[str, str]:
        return {e.new_key: e.value for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        modified = self.modified_count
        return f"{modified}/{total} keys modified"


def add_prefix(
    env: Dict[str, str],
    prefix: str,
    *,
    skip_already_prefixed: bool = True,
) -> PrefixReport:
    """Return a report where every key gains *prefix*."""
    report = PrefixReport()
    for key, value in env.items():
        if skip_already_prefixed and key.startswith(prefix):
            report.add(PrefixEntry(key, key, value, "unchanged"))
        else:
            new_key = f"{prefix}{key}"
            report.add(PrefixEntry(key, new_key, value, "added"))
    return report


def strip_prefix(
    env: Dict[str, str],
    prefix: str,
    *,
    keep_non_matching: bool = True,
) -> PrefixReport:
    """Return a report where *prefix* is removed from matching keys."""
    report = PrefixReport()
    for key, value in env.items():
        if key.startswith(prefix):
            new_key = key[len(prefix):]
            report.add(PrefixEntry(key, new_key, value, "stripped"))
        elif keep_non_matching:
            report.add(PrefixEntry(key, key, value, "unchanged"))
    return report
