"""Group environment variables by shared key prefix."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GroupEntry:
    key: str
    value: str
    prefix: str
    suffix: str

    def __str__(self) -> str:
        return f"{self.key}={self.value} (group={self.prefix})"


@dataclass
class GroupReport:
    _groups: Dict[str, List[GroupEntry]] = field(default_factory=dict)
    _ungrouped: List[GroupEntry] = field(default_factory=list)

    def add(self, entry: GroupEntry) -> None:
        if entry.prefix:
            self._groups.setdefault(entry.prefix, []).append(entry)
        else:
            self._ungrouped.append(entry)

    def group_names(self) -> List[str]:
        return sorted(self._groups.keys())

    def by_group(self, name: str) -> List[GroupEntry]:
        return self._groups.get(name, [])

    @property
    def ungrouped(self) -> List[GroupEntry]:
        return list(self._ungrouped)

    def group_count(self) -> int:
        return len(self._groups)

    def total_keys(self) -> int:
        return sum(len(v) for v in self._groups.values()) + len(self._ungrouped)

    def summary(self) -> str:
        return (
            f"{self.group_count()} group(s), "
            f"{len(self._ungrouped)} ungrouped, "
            f"{self.total_keys()} total key(s)"
        )


def _extract_prefix(key: str, separator: str = "_") -> tuple:
    """Return (prefix, suffix) by splitting on the first separator occurrence."""
    if separator in key:
        idx = key.index(separator)
        return key[:idx], key[idx + len(separator):]
    return "", key


def group_env(
    env: Dict[str, str],
    separator: str = "_",
    min_group_size: int = 1,
) -> GroupReport:
    """Group env vars by shared key prefix using *separator*.

    Keys whose prefix group has fewer than *min_group_size* members are
    placed in the ungrouped bucket.
    """
    report = GroupReport()
    prefix_map: Dict[str, List[GroupEntry]] = {}

    for key, value in env.items():
        prefix, suffix = _extract_prefix(key, separator)
        entry = GroupEntry(key=key, value=value, prefix=prefix, suffix=suffix)
        prefix_map.setdefault(prefix, []).append(entry)

    for prefix, entries in prefix_map.items():
        effective_prefix = prefix if (prefix and len(entries) >= min_group_size) else ""
        for entry in entries:
            entry.prefix = effective_prefix
            report.add(entry)

    return report
