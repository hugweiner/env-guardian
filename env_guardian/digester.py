"""Digest module: compute and compare checksums for env variable sets."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class DigestEntry:
    key: str
    value: str
    checksum: str

    def __str__(self) -> str:
        return f"{self.key}={self.checksum[:12]}..."


@dataclass
class DigestReport:
    entries: Dict[str, DigestEntry] = field(default_factory=dict)
    algorithm: str = "sha256"

    def add(self, entry: DigestEntry) -> None:
        self.entries[entry.key] = entry

    def checksum_for(self, key: str) -> Optional[str]:
        e = self.entries.get(key)
        return e.checksum if e else None

    def fingerprint(self) -> str:
        """Single checksum representing the entire env set."""
        combined = json.dumps(
            {k: e.checksum for k, e in sorted(self.entries.items())},
            sort_keys=True,
        )
        return hashlib.sha256(combined.encode()).hexdigest()

    def diff_against(self, other: "DigestReport") -> Dict[str, str]:
        """Return keys whose checksums differ between this and other report."""
        changes: Dict[str, str] = {}
        all_keys = set(self.entries) | set(other.entries)
        for key in all_keys:
            a = self.checksum_for(key)
            b = other.checksum_for(key)
            if a != b:
                changes[key] = f"{a or 'missing'} -> {b or 'missing'}"
        return changes

    def summary(self) -> str:
        return f"{len(self.entries)} key(s) digested using {self.algorithm}"


def _compute(value: str, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    h.update(value.encode())
    return h.hexdigest()


def digest_env(
    env: Dict[str, str],
    algorithm: str = "sha256",
) -> DigestReport:
    """Compute per-key checksums for all entries in *env*."""
    supported = {"sha256", "sha1", "md5"}
    if algorithm not in supported:
        raise ValueError(f"Unsupported algorithm '{algorithm}'. Choose from {supported}.")

    report = DigestReport(algorithm=algorithm)
    for key, value in env.items():
        checksum = _compute(value, algorithm)
        report.add(DigestEntry(key=key, value=value, checksum=checksum))
    return report
