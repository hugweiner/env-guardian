"""Extract a subset of environment variables by key pattern or explicit list."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional


@dataclass
class ExtractEntry:
    key: str
    value: str
    matched_by: str  # 'exact', 'pattern', or 'prefix'

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.key}={self.value!r} (matched_by={self.matched_by})"


@dataclass
class ExtractReport:
    entries: List[ExtractEntry] = field(default_factory=list)

    def add(self, entry: ExtractEntry) -> None:
        self.entries.append(entry)

    def extracted_count(self) -> int:
        return len(self.entries)

    def extracted_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def by_match_type(self, match_type: str) -> List[ExtractEntry]:
        return [e for e in self.entries if e.matched_by == match_type]

    def summary(self) -> str:
        return f"Extracted {self.extracted_count()} key(s)."


def extract_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    prefix: Optional[str] = None,
) -> ExtractReport:
    """Return an ExtractReport containing only the matching keys.

    Priority: explicit *keys* > *patterns* (fnmatch) > *prefix* match.
    If none of the selectors are provided every key is extracted.
    """
    report = ExtractReport()
    keys = keys or []
    patterns = patterns or []

    for key, value in env.items():
        matched_by: Optional[str] = None

        if key in keys:
            matched_by = "exact"
        elif any(fnmatch(key, pat) for pat in patterns):
            matched_by = "pattern"
        elif prefix and key.startswith(prefix):
            matched_by = "prefix"
        elif not keys and not patterns and prefix is None:
            matched_by = "exact"  # no filter → include all

        if matched_by is not None:
            report.add(ExtractEntry(key=key, value=value, matched_by=matched_by))

    return report
