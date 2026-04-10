"""Pin environment variable values to a lockfile for drift detection."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PinEntry:
    key: str
    value: str
    checksum: str

    def __str__(self) -> str:
        return f"{self.key}={self.checksum[:8]}…"


@dataclass
class PinReport:
    entries: List[PinEntry] = field(default_factory=list)
    drifted: List[str] = field(default_factory=list)
    new_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)

    def is_clean(self) -> bool:
        return not self.drifted and not self.new_keys and not self.removed_keys

    def summary(self) -> str:
        if self.is_clean():
            return "No drift detected."
        parts = []
        if self.drifted:
            parts.append(f"{len(self.drifted)} drifted")
        if self.new_keys:
            parts.append(f"{len(self.new_keys)} new")
        if self.removed_keys:
            parts.append(f"{len(self.removed_keys)} removed")
        return "Drift detected: " + ", ".join(parts) + "."


def _checksum(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def create_pinfile(env: Dict[str, str]) -> Dict[str, str]:
    """Return a dict mapping keys to their SHA-256 checksums."""
    return {key: _checksum(value) for key, value in env.items()}


def check_pins(
    env: Dict[str, str],
    pinfile: Dict[str, str],
) -> PinReport:
    """Compare current env against a pinfile and return a PinReport."""
    report = PinReport()

    for key, value in env.items():
        current_checksum = _checksum(value)
        entry = PinEntry(key=key, value=value, checksum=current_checksum)
        report.entries.append(entry)

        if key not in pinfile:
            report.new_keys.append(key)
        elif pinfile[key] != current_checksum:
            report.drifted.append(key)

    for pinned_key in pinfile:
        if pinned_key not in env:
            report.removed_keys.append(pinned_key)

    return report


def load_pinfile(raw: str) -> Dict[str, str]:
    """Load a pinfile from a JSON string."""
    return json.loads(raw)


def dump_pinfile(pinfile: Dict[str, str]) -> str:
    """Serialize a pinfile to a JSON string."""
    return json.dumps(pinfile, indent=2, sort_keys=True)
