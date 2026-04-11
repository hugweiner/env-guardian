"""Deduplicator: detect and remove duplicate values across env keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DuplicateGroup:
    value: str
    keys: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # noqa: D401
        keys_str = ", ".join(self.keys)
        return f"DuplicateGroup(value={self.value!r}, keys=[{keys_str}])"


@dataclass
class DeduplicateReport:
    groups: List[DuplicateGroup] = field(default_factory=list)
    deduplicated_env: Dict[str, str] = field(default_factory=dict)

    def is_clean(self) -> bool:
        """Return True when no duplicate values were found."""
        return len(self.groups) == 0

    def duplicate_count(self) -> int:
        """Total number of keys involved in at least one duplicate group."""
        return sum(len(g.keys) for g in self.groups)

    def summary(self) -> str:
        if self.is_clean():
            return "No duplicate values found."
        return (
            f"{len(self.groups)} duplicate group(s) found "
            f"affecting {self.duplicate_count()} key(s)."
        )


def deduplicate_env(
    env: Dict[str, str],
    *,
    keep: str = "first",
    ignore_empty: bool = True,
) -> DeduplicateReport:
    """Detect keys that share identical values and optionally keep one per group.

    Args:
        env: The environment mapping to inspect.
        keep: Which key to retain per group — ``'first'`` (alphabetically) or
              ``'last'``.
        ignore_empty: When *True*, empty-string values are not considered
                      duplicates of each other.

    Returns:
        A :class:`DeduplicateReport` with duplicate groups and a cleaned env.
    """
    value_map: Dict[str, List[str]] = {}
    for key, value in env.items():
        if ignore_empty and value == "":
            continue
        value_map.setdefault(value, []).append(key)

    groups: List[DuplicateGroup] = [
        DuplicateGroup(value=val, keys=sorted(keys))
        for val, keys in value_map.items()
        if len(keys) > 1
    ]

    # Build deduplicated env: for each duplicate group keep one key, drop rest.
    keys_to_drop: set = set()
    for group in groups:
        ordered = sorted(group.keys)
        drop = ordered[:-1] if keep == "last" else ordered[1:]
        keys_to_drop.update(drop)

    deduplicated = {k: v for k, v in env.items() if k not in keys_to_drop}

    return DeduplicateReport(groups=groups, deduplicated_env=deduplicated)
