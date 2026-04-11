"""Deprecation tracker — flags env keys that are known to be deprecated."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeprecationWarning_:
    key: str
    reason: str
    replacement: Optional[str] = None

    def __str__(self) -> str:
        msg = f"{self.key}: {self.reason}"
        if self.replacement:
            msg += f" (use '{self.replacement}' instead)"
        return msg


@dataclass
class DeprecateReport:
    warnings: List[DeprecationWarning_] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def add(self, warning: DeprecationWarning_) -> None:
        self.warnings.append(warning)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No deprecated keys found."
        return f"{len(self.warnings)} deprecated key(s) found."

    def deprecated_keys(self) -> List[str]:
        return [w.key for w in self.warnings]

    def by_key(self) -> Dict[str, DeprecationWarning_]:
        return {w.key: w for w in self.warnings}


# Built-in deprecation rules: key -> (reason, replacement)
_BUILTIN_RULES: Dict[str, tuple] = {
    "DB_HOST": ("Prefer DATABASE_URL for connection config", "DATABASE_URL"),
    "DB_PASS": ("Prefer DATABASE_URL for connection config", "DATABASE_URL"),
    "DB_USER": ("Prefer DATABASE_URL for connection config", "DATABASE_URL"),
    "SECRET": ("Too generic; use a namespaced secret key", "SECRET_KEY"),
    "DEBUG_MODE": ("Renamed in v2", "DEBUG"),
    "APP_ENV": ("Renamed in v2", "ENVIRONMENT"),
    "LOG_LEVEL_OVERRIDE": ("Use LOG_LEVEL directly", "LOG_LEVEL"),
}


def deprecate_env(
    env: Dict[str, str],
    extra_rules: Optional[Dict[str, tuple]] = None,
) -> DeprecateReport:
    """Check *env* against known deprecation rules.

    Parameters
    ----------
    env:
        Parsed environment dict.
    extra_rules:
        Additional ``{KEY: (reason, replacement_or_None)}`` mappings that
        supplement the built-in rules.
    """
    rules = dict(_BUILTIN_RULES)
    if extra_rules:
        rules.update(extra_rules)

    report = DeprecateReport(env=dict(env))
    for key in env:
        if key in rules:
            reason, replacement = rules[key]
            report.add(DeprecationWarning_(key=key, reason=reason, replacement=replacement))
    return report
