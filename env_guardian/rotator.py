"""Key rotation: flag stale keys and suggest rotated names."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


@dataclass
class RotateEntry:
    key: str
    value: str
    rotated_key: str
    reason: str
    stale: bool = False

    def __str__(self) -> str:  # pragma: no cover
        tag = "[STALE]" if self.stale else "[ok]"
        return f"{tag} {self.key} -> {self.rotated_key}: {self.reason}"


@dataclass
class RotateReport:
    entries: List[RotateEntry] = field(default_factory=list)
    _rotated_env: Dict[str, str] = field(default_factory=dict, repr=False)

    def add(self, entry: RotateEntry) -> None:
        self.entries.append(entry)
        self._rotated_env[entry.rotated_key] = entry.value

    @property
    def stale_count(self) -> int:
        return sum(1 for e in self.entries if e.stale)

    @property
    def rotated_env(self) -> Dict[str, str]:
        return dict(self._rotated_env)

    def is_clean(self) -> bool:
        return self.stale_count == 0

    def summary(self) -> str:
        total = len(self.entries)
        stale = self.stale_count
        return f"{total} key(s) processed, {stale} stale rotation(s) detected."


_STALE_SUFFIXES = [
    "_OLD", "_PREV", "_BACKUP", "_BAK", "_DEPRECATED", "_LEGACY", "_V1", "_V2",
]


def _is_stale(key: str) -> bool:
    upper = key.upper()
    return any(upper.endswith(s) for s in _STALE_SUFFIXES)


def _suggested_rotation(key: str, suffix: Optional[str] = None) -> str:
    year = date.today().year
    tag = suffix or str(year)
    return f"{key}_ROTATED_{tag}"


def rotate_env(
    env: Dict[str, str],
    suffix: Optional[str] = None,
    flag_stale: bool = True,
) -> RotateReport:
    report = RotateReport()
    for key, value in env.items():
        stale = flag_stale and _is_stale(key)
        rotated_key = _suggested_rotation(key, suffix)
        reason = "stale suffix detected" if stale else "scheduled rotation"
        entry = RotateEntry(
            key=key,
            value=value,
            rotated_key=rotated_key,
            reason=reason,
            stale=stale,
        )
        report.add(entry)
    return report
