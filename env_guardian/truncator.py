"""Truncate long env variable values to a maximum length."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TruncateWarning:
    key: str
    original_length: int
    truncated_length: int

    def __str__(self) -> str:
        return (
            f"{self.key}: truncated from {self.original_length} "
            f"to {self.truncated_length} chars"
        )


@dataclass
class TruncateReport:
    env: Dict[str, str] = field(default_factory=dict)
    warnings: List[TruncateWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No values truncated."
        return f"{len(self.warnings)} value(s) truncated."

    def truncated_count(self) -> int:
        return len(self.warnings)

    def truncated_keys(self) -> List[str]:
        return [w.key for w in self.warnings]


def truncate_env(
    env: Dict[str, str],
    max_length: int = 64,
    suffix: str = "...",
) -> TruncateReport:
    """Return a new env dict with values truncated to *max_length* characters.

    Values already within the limit are left unchanged.  For each truncated
    value a :class:`TruncateWarning` is recorded in the report.

    Args:
        env: Source environment mapping.
        max_length: Maximum allowed value length (must be > 0).
        suffix: Appended to truncated values; counts toward *max_length*.
    """
    if max_length <= 0:
        raise ValueError("max_length must be a positive integer")

    report = TruncateReport()

    for key, value in env.items():
        if len(value) > max_length:
            cut = max_length - len(suffix)
            if cut < 0:
                cut = 0
            new_value = value[:cut] + suffix
            report.env[key] = new_value
            report.warnings.append(
                TruncateWarning(
                    key=key,
                    original_length=len(value),
                    truncated_length=len(new_value),
                )
            )
        else:
            report.env[key] = value

    return report
