"""Trim whitespace and normalize values in an env dictionary."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TrimWarning:
    key: str
    original: str
    trimmed: str
    reason: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.reason}: {self.original!r} -> {self.trimmed!r}"


@dataclass
class TrimReport:
    env: Dict[str, str] = field(default_factory=dict)
    warnings: List[TrimWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No trimming needed."
        return f"{len(self.warnings)} value(s) trimmed."

    def trimmed_count(self) -> int:
        return len(self.warnings)

    def by_key(self, key: str) -> List[TrimWarning]:
        return [w for w in self.warnings if w.key == key]


def trim_env(
    env: Dict[str, str],
    strip_keys: bool = True,
    strip_values: bool = True,
    collapse_whitespace: bool = False,
) -> TrimReport:
    """Return a TrimReport with cleaned env and warnings for each change."""
    report = TrimReport()

    for raw_key, raw_value in env.items():
        key = raw_key.strip() if strip_keys else raw_key
        value = raw_value

        if strip_values:
            stripped = raw_value.strip()
            if stripped != raw_value:
                report.warnings.append(
                    TrimWarning(
                        key=key,
                        original=raw_value,
                        trimmed=stripped,
                        reason="leading/trailing whitespace in value",
                    )
                )
                value = stripped

        if collapse_whitespace:
            import re
            collapsed = re.sub(r"\s+", " ", value)
            if collapsed != value:
                report.warnings.append(
                    TrimWarning(
                        key=key,
                        original=value,
                        trimmed=collapsed,
                        reason="internal whitespace collapsed",
                    )
                )
                value = collapsed

        if strip_keys and raw_key != key:
            report.warnings.append(
                TrimWarning(
                    key=key,
                    original=raw_key,
                    trimmed=key,
                    reason="leading/trailing whitespace in key",
                )
            )

        report.env[key] = value

    return report
