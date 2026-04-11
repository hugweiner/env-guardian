"""Pad environment variable values to a minimum length using a fill character."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PadWarning:
    key: str
    original: str
    padded: str
    reason: str

    def __str__(self) -> str:
        return f"[PAD] {self.key}: {self.original!r} -> {self.padded!r} ({self.reason})"


@dataclass
class PadReport:
    env: Dict[str, str] = field(default_factory=dict)
    warnings: List[PadWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No padding applied."
        return f"{len(self.warnings)} value(s) padded."

    def padded_count(self) -> int:
        return len(self.warnings)


def pad_env(
    env: Dict[str, str],
    min_length: int = 8,
    fill_char: str = "0",
    align: str = "right",
    keys: Optional[List[str]] = None,
) -> PadReport:
    """Pad values in env to at least min_length characters.

    Args:
        env: Source environment dict.
        min_length: Minimum value length after padding.
        fill_char: Character used to pad (single char).
        align: 'right' pads on the left, 'left' pads on the right.
        keys: Restrict padding to these keys only; None means all keys.
    """
    if len(fill_char) != 1:
        raise ValueError("fill_char must be exactly one character")
    if align not in ("left", "right"):
        raise ValueError("align must be 'left' or 'right'")

    report = PadReport()
    for key, value in env.items():
        if keys is not None and key not in keys:
            report.env[key] = value
            continue
        if len(value) < min_length:
            pad_needed = min_length - len(value)
            padding = fill_char * pad_needed
            padded = (padding + value) if align == "right" else (value + padding)
            reason = f"length {len(value)} < min {min_length}, padded {align}"
            report.warnings.append(PadWarning(key=key, original=value, padded=padded, reason=reason))
            report.env[key] = padded
        else:
            report.env[key] = value
    return report
