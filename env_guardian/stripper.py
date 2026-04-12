"""Strip specified keys or key patterns from an env dict."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StripEntry:
    key: str
    value: str
    reason: str  # 'pattern' | 'exact'
    pattern: str

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.key} stripped (matched {self.pattern!r} via {self.reason})"


@dataclass
class StripReport:
    stripped: List[StripEntry] = field(default_factory=list)
    kept: Dict[str, str] = field(default_factory=dict)

    def add(self, entry: StripEntry) -> None:
        self.stripped.append(entry)

    @property
    def stripped_count(self) -> int:
        return len(self.stripped)

    @property
    def is_clean(self) -> bool:
        return len(self.stripped) == 0

    def summary(self) -> str:
        if self.is_clean:
            return "No keys stripped."
        return f"{self.stripped_count} key(s) stripped."


def strip_env(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    exact: Optional[List[str]] = None,
) -> StripReport:
    """Return a StripReport removing keys that match *patterns* (glob) or *exact* names.

    Args:
        env:      Source environment mapping.
        patterns: List of glob-style patterns (e.g. ``["DB_*", "*_SECRET"]``).
        exact:    List of exact key names to remove.
    """
    patterns = patterns or []
    exact_set = set(exact or [])
    report = StripReport()

    for key, value in env.items():
        matched_pattern: Optional[str] = None
        match_reason: Optional[str] = None

        if key in exact_set:
            matched_pattern = key
            match_reason = "exact"
        else:
            for pat in patterns:
                if fnmatch.fnmatch(key, pat):
                    matched_pattern = pat
                    match_reason = "pattern"
                    break

        if matched_pattern is not None:
            report.add(
                StripEntry(
                    key=key,
                    value=value,
                    reason=match_reason,  # type: ignore[arg-type]
                    pattern=matched_pattern,
                )
            )
        else:
            report.kept[key] = value

    return report
