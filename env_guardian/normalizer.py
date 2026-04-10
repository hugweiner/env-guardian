"""Normalize environment variable keys and values."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NormalizeWarning:
    key: str
    original: str
    normalized: str
    reason: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.reason}: {self.original!r} -> {self.normalized!r}"


@dataclass
class NormalizeReport:
    env: Dict[str, str] = field(default_factory=dict)
    warnings: List[NormalizeWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No normalization changes applied."
        return f"{len(self.warnings)} normalization change(s) applied."


def _normalize_key(key: str) -> str:
    """Uppercase and strip whitespace from key."""
    return key.strip().upper()


def _normalize_value(value: str) -> str:
    """Strip leading/trailing whitespace from value."""
    return value.strip()


def normalize_env(env: Dict[str, str]) -> NormalizeReport:
    """Normalize all keys and values in an env dict.

    - Keys are uppercased and stripped of whitespace.
    - Values are stripped of surrounding whitespace.
    - Duplicate keys after normalization: last occurrence wins.
    """
    report = NormalizeReport()

    for raw_key, raw_value in env.items():
        norm_key = _normalize_key(raw_key)
        norm_value = _normalize_value(raw_value)

        if norm_key != raw_key:
            report.warnings.append(
                NormalizeWarning(
                    key=norm_key,
                    original=raw_key,
                    normalized=norm_key,
                    reason="key normalized (uppercase/strip)",
                )
            )

        if norm_value != raw_value:
            report.warnings.append(
                NormalizeWarning(
                    key=norm_key,
                    original=raw_value,
                    normalized=norm_value,
                    reason="value whitespace stripped",
                )
            )

        report.env[norm_key] = norm_value

    return report
