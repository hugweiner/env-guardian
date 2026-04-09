"""Lint environment variable keys and values for style and correctness."""

from dataclasses import dataclass, field
from typing import List, Dict
import re

_RECOMMENDED_PATTERN = re.compile(r'^[A-Z][A-Z0-9_]*$')
_DOUBLE_UNDERSCORE = re.compile(r'__')
_URL_PATTERN = re.compile(r'https?://', re.IGNORECASE)
_PLACEHOLDER_PATTERN = re.compile(r'^<.*>$|^\$\{.*\}$|^CHANGE_ME$|^TODO$', re.IGNORECASE)


@dataclass
class LintWarning:
    key: str
    message: str
    severity: str  # 'error' | 'warning' | 'info'

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class LintReport:
    warnings: List[LintWarning] = field(default_factory=list)

    def add(self, key: str, message: str, severity: str = 'warning') -> None:
        self.warnings.append(LintWarning(key=key, message=message, severity=severity))

    @property
    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def by_severity(self, severity: str) -> List[LintWarning]:
        return [w for w in self.warnings if w.severity == severity]

    def summary(self) -> str:
        if self.is_clean:
            return "No lint issues found."
        counts = {}
        for w in self.warnings:
            counts[w.severity] = counts.get(w.severity, 0) + 1
        parts = [f"{v} {k}(s)" for k, v in sorted(counts.items())]
        return "Lint issues: " + ", ".join(parts)


def lint_env(env: Dict[str, str], strict: bool = False) -> LintReport:
    """Lint an environment variable dict and return a LintReport."""
    report = LintReport()

    for key, value in env.items():
        # Key naming convention
        if not _RECOMMENDED_PATTERN.match(key):
            severity = 'error' if strict else 'warning'
            report.add(key, "Key should match pattern [A-Z][A-Z0-9_]*", severity)

        # Double underscores are allowed but worth flagging
        if _DOUBLE_UNDERSCORE.search(key):
            report.add(key, "Key contains double underscore; consider simplifying", 'info')

        # Leading/trailing whitespace in value
        if value != value.strip():
            report.add(key, "Value has leading or trailing whitespace", 'warning')

        # Placeholder values
        if _PLACEHOLDER_PATTERN.match(value.strip()):
            report.add(key, "Value appears to be a placeholder and should be replaced", 'warning')

        # Hardcoded localhost URLs in non-dev keys
        if 'localhost' in value.lower() and not any(
            tag in key.upper() for tag in ('DEV', 'LOCAL', 'TEST')
        ):
            report.add(key, "Value contains 'localhost'; may not be suitable for production", 'info')

        # Very long values (possible accidental paste)
        if len(value) > 2048:
            report.add(key, f"Value is unusually long ({len(value)} chars)", 'info')

    return report
