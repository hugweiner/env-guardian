"""Duplicator: copy keys to new names within an env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DuplicateEntry:
    source_key: str
    target_key: str
    value: str
    skipped: bool = False
    skip_reason: Optional[str] = None

    def __str__(self) -> str:  # pragma: no cover
        if self.skipped:
            return f"{self.source_key} -> {self.target_key} [SKIPPED: {self.skip_reason}]"
        return f"{self.source_key} -> {self.target_key} = {self.value!r}"


@dataclass
class DuplicateReport:
    entries: List[DuplicateEntry] = field(default_factory=list)

    def add(self, entry: DuplicateEntry) -> None:
        self.entries.append(entry)

    def duplicated_count(self) -> int:
        return sum(1 for e in self.entries if not e.skipped)

    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if e.skipped)

    def result_env(self, base: Dict[str, str]) -> Dict[str, str]:
        """Return a new env dict with successful duplications applied."""
        out = dict(base)
        for e in self.entries:
            if not e.skipped:
                out[e.target_key] = e.value
        return out

    def summary(self) -> str:
        return (
            f"{self.duplicated_count()} key(s) duplicated, "
            f"{self.skipped_count()} skipped."
        )


def duplicate_env(
    env: Dict[str, str],
    mapping: Dict[str, str],
    overwrite: bool = True,
) -> DuplicateReport:
    """Duplicate keys according to *mapping* (source -> target).

    Args:
        env:       The source environment dict.
        mapping:   Dict mapping existing key names to new key names.
        overwrite: If False, skip when the target key already exists.

    Returns:
        A :class:`DuplicateReport` describing every attempted duplication.
    """
    report = DuplicateReport()

    for source_key, target_key in mapping.items():
        if source_key not in env:
            report.add(
                DuplicateEntry(
                    source_key=source_key,
                    target_key=target_key,
                    value="",
                    skipped=True,
                    skip_reason="source key not found",
                )
            )
            continue

        if not overwrite and target_key in env:
            report.add(
                DuplicateEntry(
                    source_key=source_key,
                    target_key=target_key,
                    value=env[source_key],
                    skipped=True,
                    skip_reason="target key already exists",
                )
            )
            continue

        report.add(
            DuplicateEntry(
                source_key=source_key,
                target_key=target_key,
                value=env[source_key],
            )
        )

    return report
