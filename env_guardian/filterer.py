"""Filter environment variables by pattern, prefix, or tag."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FilterEntry:
    key: str
    value: str
    matched_rule: str

    def __str__(self) -> str:
        return f"{self.key}={self.value!r}  (rule: {self.matched_rule})"


@dataclass
class FilterReport:
    entries: List[FilterEntry] = field(default_factory=list)
    excluded_keys: List[str] = field(default_factory=list)

    def add(self, entry: FilterEntry) -> None:
        self.entries.append(entry)

    def matched_count(self) -> int:
        return len(self.entries)

    def excluded_count(self) -> int:
        return len(self.excluded_keys)

    def to_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def summary(self) -> str:
        return (
            f"{self.matched_count()} key(s) matched, "
            f"{self.excluded_count()} excluded"
        )


def filter_env(
    env: Dict[str, str],
    *,
    prefixes: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    exclude_prefixes: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
) -> FilterReport:
    """Return a FilterReport containing only keys that satisfy the filter rules."""
    report = FilterReport()
    compiled_include = [re.compile(p) for p in (patterns or [])]
    compiled_exclude = [re.compile(p) for p in (exclude_patterns or [])]

    for key, value in env.items():
        # Exclusion takes priority
        excluded = False
        if exclude_prefixes and any(key.startswith(px) for px in exclude_prefixes):
            excluded = True
        if not excluded and compiled_exclude and any(r.search(key) for r in compiled_exclude):
            excluded = True

        if excluded:
            report.excluded_keys.append(key)
            continue

        # Inclusion rules (if none specified, include everything not excluded)
        matched_rule: Optional[str] = None
        if prefixes:
            for px in prefixes:
                if key.startswith(px):
                    matched_rule = f"prefix:{px}"
                    break
        if matched_rule is None and compiled_include:
            for r in compiled_include:
                if r.search(key):
                    matched_rule = f"pattern:{r.pattern}"
                    break
        if matched_rule is None and not prefixes and not compiled_include:
            matched_rule = "*"

        if matched_rule is not None:
            report.add(FilterEntry(key=key, value=value, matched_rule=matched_rule))
        else:
            report.excluded_keys.append(key)

    return report
