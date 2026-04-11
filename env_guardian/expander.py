"""Expander: expand shorthand or abbreviated env keys to full canonical names."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ExpandEntry:
    key: str
    value: str
    expanded_key: str
    was_expanded: bool
    original_key: Optional[str] = None

    def __str__(self) -> str:
        if self.was_expanded:
            return f"{self.original_key} -> {self.expanded_key}={self.value}"
        return f"{self.key}={self.value}"


@dataclass
class ExpandReport:
    entries: List[ExpandEntry] = field(default_factory=list)

    def add(self, entry: ExpandEntry) -> None:
        self.entries.append(entry)

    def expanded_count(self) -> int:
        return sum(1 for e in self.entries if e.was_expanded)

    def expanded_env(self) -> Dict[str, str]:
        return {e.expanded_key: e.value for e in self.entries}

    def is_clean(self) -> bool:
        return self.expanded_count() == 0

    def summary(self) -> str:
        total = len(self.entries)
        expanded = self.expanded_count()
        if expanded == 0:
            return f"All {total} keys are already fully expanded."
        return f"{expanded} of {total} key(s) expanded to canonical form."


# Built-in abbreviation map: shorthand -> canonical
_DEFAULT_EXPANSIONS: Dict[str, str] = {
    "DB_HOST": "DATABASE_HOST",
    "DB_PORT": "DATABASE_PORT",
    "DB_USER": "DATABASE_USER",
    "DB_PASS": "DATABASE_PASSWORD",
    "DB_NAME": "DATABASE_NAME",
    "DB_URL": "DATABASE_URL",
    "REDIS_HOST": "REDIS_HOST",
    "APP_ENV": "APPLICATION_ENVIRONMENT",
    "APP_PORT": "APPLICATION_PORT",
    "APP_KEY": "APPLICATION_SECRET_KEY",
    "LOG_LVL": "LOG_LEVEL",
    "AWS_ID": "AWS_ACCESS_KEY_ID",
    "AWS_SECRET": "AWS_SECRET_ACCESS_KEY",
}


def expand_env(
    env: Dict[str, str],
    expansions: Optional[Dict[str, str]] = None,
) -> ExpandReport:
    """Expand abbreviated keys in *env* using the given or default expansion map."""
    mapping = _DEFAULT_EXPANSIONS if expansions is None else expansions
    report = ExpandReport()
    for key, value in env.items():
        if key in mapping:
            canonical = mapping[key]
            report.add(
                ExpandEntry(
                    key=canonical,
                    value=value,
                    expanded_key=canonical,
                    was_expanded=True,
                    original_key=key,
                )
            )
        else:
            report.add(
                ExpandEntry(
                    key=key,
                    value=value,
                    expanded_key=key,
                    was_expanded=False,
                )
            )
    return report
