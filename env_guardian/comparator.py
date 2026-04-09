"""Comparator — diffs two env variable dictionaries and reports discrepancies."""

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class EnvDiff:
    """Result of comparing two env dictionaries."""

    missing_in_target: List[str] = field(default_factory=list)
    extra_in_target: List[str] = field(default_factory=list)
    value_mismatches: Dict[str, tuple] = field(default_factory=dict)  # key -> (src, tgt)

    @property
    def is_clean(self) -> bool:
        """Return True when there are no differences."""
        return (
            not self.missing_in_target
            and not self.extra_in_target
            and not self.value_mismatches
        )

    def summary(self) -> str:
        """Human-readable summary of the diff."""
        lines: List[str] = []
        if self.missing_in_target:
            lines.append("Missing in target:")
            for k in sorted(self.missing_in_target):
                lines.append(f"  - {k}")
        if self.extra_in_target:
            lines.append("Extra in target (not in source):")
            for k in sorted(self.extra_in_target):
                lines.append(f"  + {k}")
        if self.value_mismatches:
            lines.append("Value mismatches:")
            for k, (src, tgt) in sorted(self.value_mismatches.items()):
                lines.append(f"  ~ {k}: source={src!r} | target={tgt!r}")
        if not lines:
            lines.append("No differences found. Environments are in sync.")
        return "\n".join(lines)


def compare_envs(
    source: Dict[str, str],
    target: Dict[str, str],
    ignore_values: bool = False,
    ignore_keys: Set[str] | None = None,
) -> EnvDiff:
    """
    Compare source env dict against target env dict.

    Args:
        source: The reference environment (e.g. .env.example).
        target: The environment being validated.
        ignore_values: When True, only check key presence, not values.
        ignore_keys: Set of keys to skip entirely.

    Returns:
        EnvDiff instance describing all discrepancies.
    """
    skip = ignore_keys or set()
    src_keys = {k for k in source if k not in skip}
    tgt_keys = {k for k in target if k not in skip}

    diff = EnvDiff(
        missing_in_target=sorted(src_keys - tgt_keys),
        extra_in_target=sorted(tgt_keys - src_keys),
    )

    if not ignore_values:
        for key in src_keys & tgt_keys:
            if source[key] != target[key]:
                diff.value_mismatches[key] = (source[key], target[key])

    return diff
