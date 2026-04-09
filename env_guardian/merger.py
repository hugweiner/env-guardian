"""Merge multiple env files into a single unified env dict."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MergeConflict:
    key: str
    values: List[Tuple[str, str]]  # list of (source_label, value)

    def __str__(self) -> str:
        parts = ", ".join(f"{label}={value!r}" for label, value in self.values)
        return f"Conflict on '{self.key}': {parts}"


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: List[MergeConflict] = field(default_factory=list)
    sources_used: List[str] = field(default_factory=list)

    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def summary(self) -> str:
        lines = [
            f"Merged {len(self.sources_used)} source(s): {', '.join(self.sources_used)}",
            f"Total keys: {len(self.merged)}",
            f"Conflicts: {len(self.conflicts)}",
        ]
        if self.conflicts:
            lines.append("Conflict details:")
            for c in self.conflicts:
                lines.append(f"  - {c}")
        return "\n".join(lines)


def merge_envs(
    sources: List[Tuple[str, Dict[str, str]]],
    strategy: str = "last_wins",
    raise_on_conflict: bool = False,
) -> MergeResult:
    """Merge multiple env dicts into one.

    Args:
        sources: List of (label, env_dict) tuples in priority order.
        strategy: 'last_wins' keeps the last value; 'first_wins' keeps the first.
        raise_on_conflict: If True, raise ValueError when conflicts are found.

    Returns:
        MergeResult with merged env and any detected conflicts.
    """
    if strategy not in ("last_wins", "first_wins"):
        raise ValueError(f"Unknown strategy: {strategy!r}. Use 'last_wins' or 'first_wins'.")

    result = MergeResult(sources_used=[label for label, _ in sources])
    seen: Dict[str, List[Tuple[str, str]]] = {}

    for label, env in sources:
        for key, value in env.items():
            if key not in seen:
                seen[key] = []
            seen[key].append((label, value))

    for key, entries in seen.items():
        unique_values = list(dict.fromkeys(v for _, v in entries))
        if len(unique_values) > 1:
            conflict = MergeConflict(key=key, values=entries)
            result.conflicts.append(conflict)
            if raise_on_conflict:
                raise ValueError(f"Merge conflict: {conflict}")

        chosen_value = entries[-1][1] if strategy == "last_wins" else entries[0][1]
        result.merged[key] = chosen_value

    return result
