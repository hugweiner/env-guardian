"""Map environment variable keys from one name to another using a mapping dict."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class MapEntry:
    source_key: str
    target_key: str
    value: str
    skipped: bool = False
    skip_reason: Optional[str] = None

    def __str__(self) -> str:
        if self.skipped:
            return f"[SKIP] {self.source_key} -> {self.target_key}: {self.skip_reason}"
        return f"{self.source_key} -> {self.target_key} = {self.value!r}"


@dataclass
class MapReport:
    entries: list = field(default_factory=list)

    def add(self, entry: MapEntry) -> None:
        self.entries.append(entry)

    def mapped_count(self) -> int:
        return sum(1 for e in self.entries if not e.skipped)

    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if e.skipped)

    def mapped_env(self) -> Dict[str, str]:
        return {e.target_key: e.value for e in self.entries if not e.skipped}

    def summary(self) -> str:
        return (
            f"{self.mapped_count()} key(s) mapped, "
            f"{self.skipped_count()} skipped."
        )


def map_env(
    env: Dict[str, str],
    mapping: Dict[str, str],
    skip_missing: bool = True,
) -> MapReport:
    """Rename keys in *env* according to *mapping* (source -> target).

    Keys in *env* that have no entry in *mapping* are carried through unchanged
    unless *skip_missing* is False, in which case they are dropped.
    """
    report = MapReport()

    # Process explicitly mapped keys first
    mapped_sources = set()
    for source_key, target_key in mapping.items():
        if source_key not in env:
            entry = MapEntry(
                source_key=source_key,
                target_key=target_key,
                value="",
                skipped=True,
                skip_reason="source key not found in env",
            )
        else:
            entry = MapEntry(
                source_key=source_key,
                target_key=target_key,
                value=env[source_key],
            )
            mapped_sources.add(source_key)
        report.add(entry)

    # Carry through unmapped keys when skip_missing is False
    if not skip_missing:
        for key, value in env.items():
            if key not in mapped_sources:
                report.add(MapEntry(source_key=key, target_key=key, value=value))

    return report
