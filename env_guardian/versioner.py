"""Version-stamp env snapshots and detect schema drift between versions."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class VersionEntry:
    version: int
    label: str
    timestamp: str
    keys: List[str]
    schema_hash: str

    def __str__(self) -> str:
        return f"v{self.version} [{self.label}] {self.timestamp} ({len(self.keys)} keys)"


@dataclass
class SchemaDrift:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed)

    def summary(self) -> str:
        if not self.has_drift:
            return "No schema drift detected."
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)} added")
        if self.removed:
            parts.append(f"-{len(self.removed)} removed")
        return "Schema drift: " + ", ".join(parts)


@dataclass
class VersionReport:
    entries: List[VersionEntry] = field(default_factory=list)

    def latest(self) -> Optional[VersionEntry]:
        return self.entries[-1] if self.entries else None

    def version_count(self) -> int:
        return len(self.entries)

    def get(self, version: int) -> Optional[VersionEntry]:
        for e in self.entries:
            if e.version == version:
                return e
        return None


def _schema_hash(env: Dict[str, str]) -> str:
    key_str = json.dumps(sorted(env.keys()))
    return hashlib.sha256(key_str.encode()).hexdigest()[:16]


def stamp_version(
    report: VersionReport,
    env: Dict[str, str],
    label: str = "",
) -> VersionEntry:
    """Add a new version entry to *report* for the given *env* and return it."""
    next_version = (report.latest().version + 1) if report.entries else 1
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entry = VersionEntry(
        version=next_version,
        label=label or f"v{next_version}",
        timestamp=ts,
        keys=sorted(env.keys()),
        schema_hash=_schema_hash(env),
    )
    report.entries.append(entry)
    return entry


def diff_versions(a: VersionEntry, b: VersionEntry) -> SchemaDrift:
    """Compare two version entries and return schema drift."""
    set_a = set(a.keys)
    set_b = set(b.keys)
    return SchemaDrift(
        added=sorted(set_b - set_a),
        removed=sorted(set_a - set_b),
    )
