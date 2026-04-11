"""Coercer: force environment variable values into a canonical string format."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CoerceWarning:
    key: str
    original: str
    coerced: str
    reason: str

    def __str__(self) -> str:  # pragma: no cover
        return f"[COERCE] {self.key}: {self.original!r} -> {self.coerced!r} ({self.reason})"


@dataclass
class CoerceReport:
    env: Dict[str, str] = field(default_factory=dict)
    warnings: List[CoerceWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No coercions applied."
        return f"{len(self.warnings)} coercion(s) applied."

    def coerced_count(self) -> int:
        return len(self.warnings)


_BOOL_TRUE = {"1", "true", "yes", "on"}
_BOOL_FALSE = {"0", "false", "no", "off"}


def _coerce_value(value: str) -> tuple[str, Optional[str]]:
    """Return (canonical_value, reason) or (value, None) if no change needed."""
    stripped = value.strip()

    # Normalise booleans
    lower = stripped.lower()
    if lower in _BOOL_TRUE:
        canonical = "true"
        if stripped != canonical:
            return canonical, f"boolean normalised from {stripped!r}"
        return value, None
    if lower in _BOOL_FALSE:
        canonical = "false"
        if stripped != canonical:
            return canonical, f"boolean normalised from {stripped!r}"
        return value, None

    # Strip surrounding whitespace
    if stripped != value:
        return stripped, "surrounding whitespace removed"

    # Collapse internal multiple spaces
    collapsed = " ".join(stripped.split())
    if collapsed != stripped:
        return collapsed, "internal whitespace collapsed"

    return value, None


def coerce_env(
    env: Dict[str, str],
    *,
    normalize_bools: bool = True,
    strip_whitespace: bool = True,
    collapse_spaces: bool = True,
) -> CoerceReport:
    """Apply canonical coercions to *env* values and return a CoerceReport."""
    report = CoerceReport()
    for key, value in env.items():
        canonical, reason = _coerce_value(value)
        if reason is not None:
            report.warnings.append(
                CoerceWarning(key=key, original=value, coerced=canonical, reason=reason)
            )
            report.env[key] = canonical
        else:
            report.env[key] = value
    return report
