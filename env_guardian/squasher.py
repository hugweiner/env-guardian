"""Squash duplicate values across an env dict, keeping one canonical key per unique value."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SquashGroup:
    """A group of keys that share the same value."""

    value: str
    canonical_key: str
    duplicate_keys: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        dupes = ", ".join(self.duplicate_keys)
        return f"{self.canonical_key} (value={self.value!r}, duplicates=[{dupes}])"


@dataclass
class SquashReport:
    groups: List[SquashGroup] = field(default_factory=list)
    squashed_env: Dict[str, str] = field(default_factory=dict)

    def is_clean(self) -> bool:
        """Return True when no duplicate values were found."""
        return all(len(g.duplicate_keys) == 0 for g in self.groups)

    def duplicate_count(self) -> int:
        """Total number of keys removed as duplicates."""
        return sum(len(g.duplicate_keys) for g in self.groups)

    def summary(self) -> str:
        if self.is_clean():
            return "No duplicate values found."
        return (
            f"{self.duplicate_count()} duplicate key(s) squashed across "
            f"{len([g for g in self.groups if g.duplicate_keys])} value group(s)."
        )


def squash_env(
    env: Dict[str, str],
    strategy: str = "first",
) -> SquashReport:
    """Squash keys that share identical values.

    Args:
        env: The environment mapping to process.
        strategy: ``'first'`` keeps the alphabetically first key as canonical;
                  ``'last'`` keeps the alphabetically last key.

    Returns:
        A :class:`SquashReport` containing groups and the de-duplicated env.
    """
    if strategy not in ("first", "last"):
        raise ValueError(f"Unknown strategy {strategy!r}. Use 'first' or 'last'.")

    # Bucket keys by value
    value_to_keys: Dict[str, List[str]] = {}
    for key, value in env.items():
        value_to_keys.setdefault(value, []).append(key)

    groups: List[SquashGroup] = []
    squashed_env: Dict[str, str] = {}

    for value, keys in value_to_keys.items():
        sorted_keys = sorted(keys)
        canonical = sorted_keys[0] if strategy == "first" else sorted_keys[-1]
        duplicates = [k for k in sorted_keys if k != canonical]
        groups.append(SquashGroup(value=value, canonical_key=canonical, duplicate_keys=duplicates))
        squashed_env[canonical] = value

    report = SquashReport(groups=groups, squashed_env=squashed_env)
    return report
