"""Generates human-readable diff reports between two env snapshots."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from env_guardian.comparator import EnvDiff, compare_envs


@dataclass
class DiffLine:
    key: str
    status: str  # 'added', 'removed', 'changed', 'unchanged'
    source_value: Optional[str] = None
    target_value: Optional[str] = None

    def __str__(self) -> str:
        if self.status == "added":
            return f"+ {self.key}={self.target_value}"
        if self.status == "removed":
            return f"- {self.key}={self.source_value}"
        if self.status == "changed":
            return f"~ {self.key}: {self.source_value!r} -> {self.target_value!r}"
        return f"  {self.key}={self.source_value}"


@dataclass
class DiffReport:
    lines: List[DiffLine] = field(default_factory=list)

    @property
    def added(self) -> List[DiffLine]:
        return [l for l in self.lines if l.status == "added"]

    @property
    def removed(self) -> List[DiffLine]:
        return [l for l in self.lines if l.status == "removed"]

    @property
    def changed(self) -> List[DiffLine]:
        return [l for l in self.lines if l.status == "changed"]

    @property
    def unchanged(self) -> List[DiffLine]:
        return [l for l in self.lines if l.status == "unchanged"]

    def is_clean(self) -> bool:
        return not self.added and not self.removed and not self.changed

    def summary(self) -> str:
        return (
            f"+{len(self.added)} added, "
            f"-{len(self.removed)} removed, "
            f"~{len(self.changed)} changed, "
            f"{len(self.unchanged)} unchanged"
        )


def build_diff_report(
    source: Dict[str, str],
    target: Dict[str, str],
    ignore_values: bool = False,
) -> DiffReport:
    """Build a DiffReport comparing source env to target env."""
    diff: EnvDiff = compare_envs(source, target, ignore_values=ignore_values)
    report = DiffReport()

    all_keys = sorted(set(source) | set(target))
    for key in all_keys:
        if key in diff.extra_keys:
            report.lines.append(DiffLine(key, "added", target_value=target.get(key)))
        elif key in diff.missing_keys:
            report.lines.append(DiffLine(key, "removed", source_value=source.get(key)))
        elif key in diff.mismatched_keys:
            report.lines.append(
                DiffLine(key, "changed", source_value=source.get(key), target_value=target.get(key))
            )
        else:
            report.lines.append(DiffLine(key, "unchanged", source_value=source.get(key)))

    return report
