"""Sync environment variables from a source to a target env file."""

from pathlib import Path
from typing import Optional

from env_guardian.comparator import compare_envs, EnvDiff
from env_guardian.parser import parse_env_file, parse_env_string


class SyncResult:
    """Holds the outcome of a sync operation."""

    def __init__(self) -> None:
        self.added: dict[str, str] = {}
        self.updated: dict[str, str] = {}
        self.removed: list[str] = []
        self.skipped: list[str] = []

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.updated or self.removed)

    def summary(self) -> str:
        lines = []
        if self.added:
            lines.append(f"Added ({len(self.added)}): {', '.join(self.added)}")
        if self.updated:
            lines.append(f"Updated ({len(self.updated)}): {', '.join(self.updated)}")
        if self.removed:
            lines.append(f"Removed ({len(self.removed)}): {', '.join(self.removed)}")
        if self.skipped:
            lines.append(f"Skipped ({len(self.skipped)}): {', '.join(self.skipped)}")
        if not lines:
            return "No changes."
        return "\n".join(lines)


def sync_envs(
    source: dict[str, str],
    target: dict[str, str],
    overwrite: bool = True,
    remove_extra: bool = False,
    ignore_keys: Optional[list[str]] = None,
) -> tuple[dict[str, str], SyncResult]:
    """Merge source into target, returning updated env and a SyncResult."""
    ignore = set(ignore_keys or [])
    result = SyncResult()
    merged = dict(target)

    for key, value in source.items():
        if key in ignore:
            result.skipped.append(key)
            continue
        if key not in merged:
            merged[key] = value
            result.added[key] = value
        elif merged[key] != value:
            if overwrite:
                merged[key] = value
                result.updated[key] = value
            else:
                result.skipped.append(key)

    if remove_extra:
        for key in list(merged):
            if key not in source and key not in ignore:
                del merged[key]
                result.removed.append(key)

    return merged, result


def sync_env_files(
    source_path: str,
    target_path: str,
    overwrite: bool = True,
    remove_extra: bool = False,
    ignore_keys: Optional[list[str]] = None,
) -> tuple[dict[str, str], SyncResult]:
    """Load two env files and sync source into target."""
    source = parse_env_file(source_path)
    target = parse_env_file(target_path) if Path(target_path).exists() else {}
    return sync_envs(source, target, overwrite=overwrite, remove_extra=remove_extra, ignore_keys=ignore_keys)
