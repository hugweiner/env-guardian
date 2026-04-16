"""Select a subset of env keys by various strategies."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SelectEntry:
    key: str
    value: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}={self.value!r} ({self.reason})"


@dataclass
class SelectReport:
    entries: List[SelectEntry] = field(default_factory=list)

    def add(self, key: str, value: str, reason: str) -> None:
        self.entries.append(SelectEntry(key=key, value=value, reason=reason))

    @property
    def selected_count(self) -> int:
        return len(self.entries)

    @property
    def selected_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def keys(self) -> List[str]:
        return [e.key for e in self.entries]

    def summary(self) -> str:
        return f"{self.selected_count} key(s) selected"


def select_env(
    env: Dict[str, str],
    *,
    keys: Optional[List[str]] = None,
    prefix: Optional[str] = None,
    suffix: Optional[str] = None,
    contains: Optional[str] = None,
) -> SelectReport:
    """Return a SelectReport containing only the keys that match the criteria.

    If no criteria are given every key is selected.
    Multiple criteria are OR-combined.
    """
    report = SelectReport()
    no_filter = keys is None and prefix is None and suffix is None and contains is None

    for k, v in env.items():
        reasons: List[str] = []
        if no_filter:
            reasons.append("all")
        else:
            if keys is not None and k in keys:
                reasons.append("key-match")
            if prefix is not None and k.startswith(prefix):
                reasons.append(f"prefix:{prefix}")
            if suffix is not None and k.endswith(suffix):
                reasons.append(f"suffix:{suffix}")
            if contains is not None and contains in k:
                reasons.append(f"contains:{contains}")
        if reasons:
            report.add(k, v, ",".join(reasons))

    return report
