"""Rename keys in an env dict according to a mapping, tracking changes."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RenameEntry:
    old_key: str
    new_key: str
    value: str
    skipped: bool = False
    skip_reason: Optional[str] = None

    def __str__(self) -> str:
        if self.skipped:
            return f"SKIP  {self.old_key} -> {self.new_key}: {self.skip_reason}"
        return f"RENAME {self.old_key} -> {self.new_key}"


@dataclass
class RenameReport:
    entries: List[RenameEntry] = field(default_factory=list)
    result_env: Dict[str, str] = field(default_factory=dict)

    def add(self, entry: RenameEntry) -> None:
        self.entries.append(entry)

    def renamed_count(self) -> int:
        return sum(1 for e in self.entries if not e.skipped)

    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if e.skipped)

    def is_clean(self) -> bool:
        return self.renamed_count() == 0

    def summary(self) -> str:
        return (
            f"{self.renamed_count()} key(s) renamed, "
            f"{self.skipped_count()} skipped."
        )


def rename_keys(
    env: Dict[str, str],
    mapping: Dict[str, str],
    overwrite: bool = False,
) -> RenameReport:
    """Rename keys in *env* according to *mapping* (old -> new).

    Args:
        env: Source environment dict.
        mapping: Dict of {old_key: new_key} rename pairs.
        overwrite: If True, overwrite new_key if it already exists in env.

    Returns:
        RenameReport with the updated env and per-key details.
    """
    report = RenameReport()
    result = dict(env)

    for old_key, new_key in mapping.items():
        if old_key not in env:
            report.add(
                RenameEntry(
                    old_key=old_key,
                    new_key=new_key,
                    value="",
                    skipped=True,
                    skip_reason="source key not found",
                )
            )
            continue

        if new_key in result and not overwrite:
            report.add(
                RenameEntry(
                    old_key=old_key,
                    new_key=new_key,
                    value=env[old_key],
                    skipped=True,
                    skip_reason="target key already exists",
                )
            )
            continue

        value = result.pop(old_key)
        result[new_key] = value
        report.add(RenameEntry(old_key=old_key, new_key=new_key, value=value))

    report.result_env = result
    return report
