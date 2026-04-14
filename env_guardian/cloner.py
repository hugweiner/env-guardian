"""Clone an env dict with optional key transformations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CloneWarning:
    key: str
    reason: str

    def __str__(self) -> str:
        return f"[WARN] {self.key}: {self.reason}"


@dataclass
class CloneReport:
    cloned_env: Dict[str, str] = field(default_factory=dict)
    warnings: List[CloneWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        total = len(self.cloned_env)
        warn = len(self.warnings)
        return f"{total} key(s) cloned, {warn} warning(s)"

    def add_warning(self, key: str, reason: str) -> None:
        self.warnings.append(CloneWarning(key=key, reason=reason))


def clone_env(
    env: Dict[str, str],
    *,
    prefix: Optional[str] = None,
    strip_prefix: Optional[str] = None,
    uppercase_keys: bool = False,
    exclude_keys: Optional[List[str]] = None,
) -> CloneReport:
    """Clone *env*, applying optional transformations.

    Args:
        env: Source environment mapping.
        prefix: Prefix to add to every cloned key.
        strip_prefix: Prefix to remove from each key before cloning.
        uppercase_keys: When True, keys are uppercased.
        exclude_keys: List of keys to omit from the clone.
    """
    report = CloneReport()
    excluded = set(exclude_keys or [])

    for key, value in env.items():
        if key in excluded:
            continue

        new_key = key

        if strip_prefix and new_key.startswith(strip_prefix):
            new_key = new_key[len(strip_prefix):]
            if not new_key:
                report.add_warning(key, "key became empty after stripping prefix; skipped")
                continue

        if uppercase_keys:
            new_key = new_key.upper()

        if prefix:
            new_key = prefix + new_key

        if new_key in report.cloned_env:
            report.add_warning(key, f"collision on cloned key '{new_key}'; overwritten")

        report.cloned_env[new_key] = value

    return report
