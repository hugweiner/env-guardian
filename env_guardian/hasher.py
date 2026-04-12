"""Hasher: compute and compare environment variable hashes for integrity checks."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class HashEntry:
    key: str
    value: str
    algorithm: str
    digest: str

    def __str__(self) -> str:
        return f"{self.key} [{self.algorithm}] {self.digest}"


@dataclass
class HashReport:
    entries: List[HashEntry] = field(default_factory=list)
    algorithm: str = "sha256"

    def add(self, entry: HashEntry) -> None:
        self.entries.append(entry)

    def digest_for(self, key: str) -> Optional[str]:
        for e in self.entries:
            if e.key == key:
                return e.digest
        return None

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.digest for e in self.entries}

    def mismatches(self, other: "HashReport") -> List[str]:
        """Return keys whose digests differ between this report and another."""
        other_map = other.as_dict()
        return [
            e.key
            for e in self.entries
            if e.key in other_map and other_map[e.key] != e.digest
        ]

    def summary(self) -> str:
        return f"{len(self.entries)} key(s) hashed with {self.algorithm}"


def _compute_digest(value: str, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    h.update(value.encode())
    return h.hexdigest()


def hash_env(
    env: Dict[str, str],
    algorithm: str = "sha256",
) -> HashReport:
    """Hash every value in *env* using *algorithm* and return a HashReport."""
    report = HashReport(algorithm=algorithm)
    for key in sorted(env):
        digest = _compute_digest(env[key], algorithm)
        report.add(HashEntry(key=key, value=env[key], algorithm=algorithm, digest=digest))
    return report
