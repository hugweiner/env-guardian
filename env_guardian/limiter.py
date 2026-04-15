"""Limiter: enforce min/max length constraints on env var values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class LimitViolation:
    key: str
    value: str
    min_length: Optional[int]
    max_length: Optional[int]
    actual_length: int
    kind: str  # 'too_short' | 'too_long'

    def __str__(self) -> str:
        if self.kind == "too_short":
            return (
                f"{self.key}: value too short "
                f"(len={self.actual_length}, min={self.min_length})"
            )
        return (
            f"{self.key}: value too long "
            f"(len={self.actual_length}, max={self.max_length})"
        )


@dataclass
class LimitReport:
    violations: List[LimitViolation] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def is_clean(self) -> bool:
        return len(self.violations) == 0

    def violation_count(self) -> int:
        return len(self.violations)

    def summary(self) -> str:
        if self.is_clean():
            return "All values within length limits."
        return (
            f"{self.violation_count()} violation(s) found: "
            + ", ".join(str(v) for v in self.violations)
        )


def limit_env(
    env: Dict[str, str],
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    per_key: Optional[Dict[str, Dict[str, int]]] = None,
) -> LimitReport:
    """Validate value lengths. per_key overrides global min/max per key."""
    report = LimitReport(env=dict(env))
    per_key = per_key or {}

    for key, value in env.items():
        key_min = per_key.get(key, {}).get("min", min_length)
        key_max = per_key.get(key, {}).get("max", max_length)
        length = len(value)

        if key_min is not None and length < key_min:
            report.violations.append(
                LimitViolation(
                    key=key,
                    value=value,
                    min_length=key_min,
                    max_length=key_max,
                    actual_length=length,
                    kind="too_short",
                )
            )
        elif key_max is not None and length > key_max:
            report.violations.append(
                LimitViolation(
                    key=key,
                    value=value,
                    min_length=key_min,
                    max_length=key_max,
                    actual_length=length,
                    kind="too_long",
                )
            )

    return report
