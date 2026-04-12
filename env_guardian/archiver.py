"""Archive env snapshots to a simple JSON-lines store."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class ArchiveEntry:
    label: str
    timestamp: str
    env: Dict[str, str]

    def __str__(self) -> str:  # pragma: no cover
        return f"ArchiveEntry(label={self.label!r}, ts={self.timestamp})"


@dataclass
class ArchiveStore:
    path: str
    entries: List[ArchiveEntry] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    @property
    def count(self) -> int:
        return len(self.entries)

    def latest(self) -> Optional[ArchiveEntry]:
        return self.entries[-1] if self.entries else None

    def by_label(self, label: str) -> List[ArchiveEntry]:
        return [e for e in self.entries if e.label == label]

    def summary(self) -> str:
        return f"{self.count} archive(s) in '{self.path}'"


# ---------------------------------------------------------------------- #

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def archive_env(
    env: Dict[str, str],
    label: str,
    path: str,
    *,
    timestamp: Optional[str] = None,
) -> ArchiveEntry:
    """Append *env* to the JSON-lines archive at *path* and return the entry."""
    ts = timestamp or _now_iso()
    entry = ArchiveEntry(label=label, timestamp=ts, env=dict(env))
    record = {"label": entry.label, "timestamp": entry.timestamp, "env": entry.env}
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    return entry


def load_archive(path: str) -> ArchiveStore:
    """Load all entries from a JSON-lines archive file."""
    store = ArchiveStore(path=path)
    if not os.path.exists(path):
        return store
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            store.entries.append(
                ArchiveEntry(
                    label=record["label"],
                    timestamp=record["timestamp"],
                    env=record["env"],
                )
            )
    return store
