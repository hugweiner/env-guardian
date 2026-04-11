"""Freeze an env dict into an immutable snapshot and detect thaw violations."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FreezeViolation:
    key: str
    expected: str
    actual: str
    reason: str

    def __str__(self) -> str:
        return f"[VIOLATION] {self.key}: {self.reason} (expected={self.expected!r}, actual={self.actual!r})"


@dataclass
class FreezeReport:
    frozen_env: Dict[str, str]
    checksum: str
    violations: List[FreezeViolation] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.violations) == 0

    def violation_count(self) -> int:
        return len(self.violations)

    def summary(self) -> str:
        if self.is_clean():
            return f"Frozen env is intact. {len(self.frozen_env)} keys verified."
        return (
            f"{self.violation_count()} violation(s) detected across "
            f"{len(self.frozen_env)} frozen key(s)."
        )


def _compute_checksum(env: Dict[str, str]) -> str:
    """Compute a deterministic SHA-256 checksum for a given env dict."""
    serialized = json.dumps(env, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def freeze_env(env: Dict[str, str]) -> FreezeReport:
    """Freeze the environment, recording a checksum of the current state."""
    checksum = _compute_checksum(env)
    return FreezeReport(frozen_env=dict(env), checksum=checksum)


def check_frozen(
    report: FreezeReport,
    current_env: Dict[str, str],
    allow_extra: bool = False,
) -> FreezeReport:
    """Compare *current_env* against a previously frozen report.

    Args:
        report: The original FreezeReport produced by :func:`freeze_env`.
        current_env: The env dict to validate against the frozen state.
        allow_extra: When *True*, keys present in *current_env* but absent
            from the frozen env are not flagged as violations.

    Returns:
        A new :class:`FreezeReport` populated with any violations found.
    """
    violations: List[FreezeViolation] = []

    for key, expected_val in report.frozen_env.items():
        if key not in current_env:
            violations.append(
                FreezeViolation(
                    key=key,
                    expected=expected_val,
                    actual="<missing>",
                    reason="key removed from env",
                )
            )
        elif current_env[key] != expected_val:
            violations.append(
                FreezeViolation(
                    key=key,
                    expected=expected_val,
                    actual=current_env[key],
                    reason="value changed",
                )
            )

    if not allow_extra:
        for key in current_env:
            if key not in report.frozen_env:
                violations.append(
                    FreezeViolation(
                        key=key,
                        expected="<absent>",
                        actual=current_env[key],
                        reason="unexpected key added to env",
                    )
                )

    return FreezeReport(
        frozen_env=report.frozen_env,
        checksum=report.checksum,
        violations=violations,
    )
