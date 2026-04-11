"""Flatten nested key structures (e.g. APP__DB__HOST -> APP_DB_HOST) in env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FlattenWarning:
    key: str
    original: str
    flattened: str
    reason: str

    def __str__(self) -> str:
        return f"[FLATTEN] {self.key}: '{self.original}' -> '{self.flattened}' ({self.reason})"


@dataclass
class FlattenReport:
    env: Dict[str, str] = field(default_factory=dict)
    warnings: List[FlattenWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No keys were flattened."
        return f"{len(self.warnings)} key(s) flattened."

    def add_warning(self, key: str, original: str, flattened: str, reason: str) -> None:
        self.warnings.append(FlattenWarning(key=key, original=original, flattened=flattened, reason=reason))


def flatten_env(
    env: Dict[str, str],
    separator: str = "__",
    replacement: str = "_",
    collision: str = "last",
) -> FlattenReport:
    """Flatten keys containing *separator* by replacing it with *replacement*.

    Args:
        env: Input environment mapping.
        separator: Multi-char (or single-char) separator to detect and replace.
        replacement: String to substitute in place of *separator*.
        collision: Strategy when two source keys map to the same flattened key.
                   ``'last'`` keeps the last value seen; ``'first'`` keeps the first.

    Returns:
        A :class:`FlattenReport` with the processed env and any warnings.
    """
    if not separator:
        raise ValueError("separator must not be empty")

    report = FlattenReport()
    seen: Dict[str, str] = {}  # flattened_key -> original_key

    for original_key, value in env.items():
        if separator in original_key:
            flat_key = original_key.replace(separator, replacement)
            reason = f"replaced '{separator}' with '{replacement}'"

            if flat_key in seen:
                prev_original = seen[flat_key]
                if collision == "first":
                    report.add_warning(original_key, original_key, flat_key,
                                       f"collision with '{prev_original}' — skipped (first-wins)")
                    continue
                else:
                    report.add_warning(original_key, original_key, flat_key,
                                       f"collision with '{prev_original}' — overwritten (last-wins)")

            report.add_warning(original_key, original_key, flat_key, reason)
            report.env[flat_key] = value
            seen[flat_key] = original_key
        else:
            report.env[original_key] = value

    return report
