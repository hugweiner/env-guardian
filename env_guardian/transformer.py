"""Transform environment variable keys and values using common normalization rules."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TransformWarning:
    key: str
    original: str
    transformed: str
    reason: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.reason}: {self.original!r} -> {self.transformed!r}"


@dataclass
class TransformReport:
    env: Dict[str, str] = field(default_factory=dict)
    warnings: List[TransformWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No transformations applied."
        return f"{len(self.warnings)} transformation(s) applied."

    def add_warning(self, key: str, original: str, transformed: str, reason: str) -> None:
        self.warnings.append(TransformWarning(key, original, transformed, reason))


def _strip_whitespace(value: str) -> Optional[str]:
    stripped = value.strip()
    return stripped if stripped != value else None


def _uppercase_key(key: str) -> Optional[str]:
    upper = key.upper()
    return upper if upper != key else None


def _remove_trailing_slash(value: str) -> Optional[str]:
    if value.endswith("/") and len(value) > 1:
        return value.rstrip("/")
    return None


def transform_env(
    env: Dict[str, str],
    uppercase_keys: bool = True,
    strip_values: bool = True,
    remove_trailing_slashes: bool = False,
) -> TransformReport:
    """Apply a series of transformations to an env dict and return a TransformReport."""
    report = TransformReport()
    result: Dict[str, str] = {}

    for raw_key, raw_value in env.items():
        key = raw_key
        value = raw_value

        if uppercase_keys:
            new_key = _uppercase_key(key)
            if new_key is not None:
                report.add_warning(new_key, key, new_key, "key uppercased")
                key = new_key

        if strip_values:
            new_value = _strip_whitespace(value)
            if new_value is not None:
                report.add_warning(key, value, new_value, "value whitespace stripped")
                value = new_value

        if remove_trailing_slashes:
            new_value = _remove_trailing_slash(value)
            if new_value is not None:
                report.add_warning(key, value, new_value, "trailing slash removed")
                value = new_value

        result[key] = value

    report.env = result
    return report
