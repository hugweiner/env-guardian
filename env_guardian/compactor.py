"""Compactor: remove keys with empty or whitespace-only values from an env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CompactWarning:
    key: str
    original_value: str

    def __str__(self) -> str:  # pragma: no cover
        return f"[REMOVED] {self.key!r} had empty/blank value"


@dataclass
class CompactReport:
    compacted_env: Dict[str, str] = field(default_factory=dict)
    warnings: List[CompactWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def removed_count(self) -> int:
        return len(self.warnings)

    def summary(self) -> str:
        total = len(self.compacted_env) + len(self.warnings)
        return (
            f"{total} keys scanned; "
            f"{len(self.warnings)} removed, "
            f"{len(self.compacted_env)} retained."
        )


def compact_env(
    env: Dict[str, str],
    *,
    strip: bool = True,
) -> CompactReport:
    """Return a new env with blank/empty values removed.

    Args:
        env:   Input environment mapping.
        strip: When *True* (default) treat whitespace-only values as empty.

    Returns:
        A :class:`CompactReport` containing the cleaned env and any warnings.
    """
    report = CompactReport()
    for key, value in env.items():
        effective = value.strip() if strip else value
        if effective == "":
            report.warnings.append(CompactWarning(key=key, original_value=value))
        else:
            report.compacted_env[key] = value
    return report
