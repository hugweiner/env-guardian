"""Snapshot module: capture and compare env state over time."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class SnapshotEntry:
    key: str
    value: str
    captured_at: str

    def __str__(self) -> str:
        return f"{self.key}={self.value!r} @ {self.captured_at}"


@dataclass
class Snapshot:
    label: str
    entries: Dict[str, SnapshotEntry] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def env(self) -> Dict[str, str]:
        return {k: e.value for k, e in self.entries.items()}

    def keys(self) -> List[str]:
        return sorted(self.entries.keys())


@dataclass
class SnapshotDiff:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    def is_clean(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        return ", ".join(parts) if parts else "no changes"


def take_snapshot(env: Dict[str, str], label: str) -> Snapshot:
    """Capture current env state as a named snapshot."""
    now = datetime.now(timezone.utc).isoformat()
    snap = Snapshot(label=label)
    for key, value in env.items():
        snap.entries[key] = SnapshotEntry(key=key, value=value, captured_at=now)
    return snap


def diff_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    """Compare two snapshots and return a SnapshotDiff."""
    diff = SnapshotDiff()
    old_env = old.env
    new_env = new.env

    for key, value in new_env.items():
        if key not in old_env:
            diff.added[key] = value
        elif old_env[key] != value:
            diff.changed[key] = (old_env[key], value)

    for key, value in old_env.items():
        if key not in new_env:
            diff.removed[key] = value

    return diff


def snapshot_to_dict(snap: Snapshot) -> dict:
    return {
        "label": snap.label,
        "created_at": snap.created_at,
        "entries": {
            k: {"value": e.value, "captured_at": e.captured_at}
            for k, e in snap.entries.items()
        },
    }


def snapshot_from_dict(data: dict) -> Snapshot:
    snap = Snapshot(label=data["label"], created_at=data["created_at"])
    for key, meta in data.get("entries", {}).items():
        snap.entries[key] = SnapshotEntry(
            key=key, value=meta["value"], captured_at=meta["captured_at"]
        )
    return snap
