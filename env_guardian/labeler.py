"""Label env keys with custom or auto-detected tags for documentation and tooling."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_BUILTIN_LABELS: Dict[str, str] = {
    "DATABASE_URL": "database",
    "DB_HOST": "database",
    "DB_PORT": "database",
    "DB_NAME": "database",
    "DB_USER": "database",
    "DB_PASSWORD": "secret",
    "SECRET_KEY": "secret",
    "API_KEY": "secret",
    "AUTH_TOKEN": "secret",
    "REDIS_URL": "cache",
    "CACHE_URL": "cache",
    "LOG_LEVEL": "logging",
    "LOG_FORMAT": "logging",
    "DEBUG": "feature-flag",
    "ENVIRONMENT": "meta",
    "APP_ENV": "meta",
    "PORT": "network",
    "HOST": "network",
}

_PREFIX_LABELS: Dict[str, str] = {
    "DB_": "database",
    "DATABASE_": "database",
    "REDIS_": "cache",
    "CACHE_": "cache",
    "LOG_": "logging",
    "AWS_": "cloud",
    "GCP_": "cloud",
    "AZURE_": "cloud",
    "SECRET_": "secret",
    "API_": "secret",
}


@dataclass
class LabelEntry:
    key: str
    value: str
    label: Optional[str]
    source: str  # 'custom', 'builtin', 'prefix', or 'none'

    def __str__(self) -> str:
        label_str = self.label or "(none)"
        return f"{self.key}={self.value!r} [{label_str} via {self.source}]"


@dataclass
class LabelReport:
    entries: List[LabelEntry] = field(default_factory=list)

    def add(self, entry: LabelEntry) -> None:
        self.entries.append(entry)

    def labeled_count(self) -> int:
        return sum(1 for e in self.entries if e.label is not None)

    def by_label(self) -> Dict[str, List[LabelEntry]]:
        groups: Dict[str, List[LabelEntry]] = {}
        for entry in self.entries:
            key = entry.label or "(none)"
            groups.setdefault(key, []).append(entry)
        return groups

    def label_names(self) -> List[str]:
        return sorted({e.label for e in self.entries if e.label is not None})

    def summary(self) -> str:
        total = len(self.entries)
        labeled = self.labeled_count()
        return f"{labeled}/{total} keys labeled across {len(self.label_names())} label(s)"


def label_env(
    env: Dict[str, str],
    custom_labels: Optional[Dict[str, str]] = None,
) -> LabelReport:
    """Assign labels to each key in *env*.

    Resolution order (highest priority first):
    1. custom_labels provided by the caller
    2. exact-match builtins
    3. prefix-based builtins
    """
    report = LabelReport()
    custom = custom_labels or {}

    for key, value in env.items():
        if key in custom:
            entry = LabelEntry(key=key, value=value, label=custom[key], source="custom")
        elif key in _BUILTIN_LABELS:
            entry = LabelEntry(key=key, value=value, label=_BUILTIN_LABELS[key], source="builtin")
        else:
            prefix_label: Optional[str] = None
            for prefix, lbl in _PREFIX_LABELS.items():
                if key.startswith(prefix):
                    prefix_label = lbl
                    break
            if prefix_label is not None:
                entry = LabelEntry(key=key, value=value, label=prefix_label, source="prefix")
            else:
                entry = LabelEntry(key=key, value=value, label=None, source="none")
        report.add(entry)

    return report
