"""Sanitize environment variable values by removing or replacing unsafe characters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class SanitizeWarning:
    key: str
    original: str
    sanitized: str
    reason: str

    def __str__(self) -> str:  # noqa: D105
        return f"[{self.key}] {self.reason}: {self.original!r} -> {self.sanitized!r}"


@dataclass
class SanitizeReport:
    warnings: List[SanitizeWarning] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "All values are clean."
        return f"{len(self.warnings)} value(s) sanitized."

    def add_warning(self, key: str, original: str, sanitized: str, reason: str) -> None:
        self.warnings.append(SanitizeWarning(key, original, sanitized, reason))


_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]")
_NULL_BYTE_RE = re.compile(r"\x00")


def _sanitize_value(value: str, strip_control: bool, strip_null: bool) -> tuple[str, Optional[str]]:
    """Return (sanitized_value, reason) or (original, None) if unchanged."""
    result = value
    reasons = []

    if strip_null and _NULL_BYTE_RE.search(result):
        result = _NULL_BYTE_RE.sub("", result)
        reasons.append("null bytes removed")

    if strip_control and _CONTROL_CHAR_RE.search(result):
        result = _CONTROL_CHAR_RE.sub("", result)
        reasons.append("control characters removed")

    if result != value:
        return result, "; ".join(reasons)
    return value, None


def sanitize_env(
    env: Dict[str, str],
    strip_control: bool = True,
    strip_null: bool = True,
) -> SanitizeReport:
    """Sanitize all values in *env* and return a :class:`SanitizeReport`."""
    report = SanitizeReport()
    for key, value in env.items():
        sanitized, reason = _sanitize_value(value, strip_control=strip_control, strip_null=strip_null)
        report.env[key] = sanitized
        if reason is not None:
            report.add_warning(key, value, sanitized, reason)
    return report
