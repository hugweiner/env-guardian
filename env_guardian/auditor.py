"""Audit environment variables for security and quality issues."""

from dataclasses import dataclass, field
from typing import List, Dict
import re

SECRET_PATTERNS = [
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"private[_-]?key", re.IGNORECASE),
]

WEAK_VALUE_PATTERNS = [
    re.compile(r"^(password|secret|123|test|example|changeme|placeholder)$", re.IGNORECASE),
]


@dataclass
class AuditIssue:
    key: str
    severity: str  # "high", "medium", "low"
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.key}: {self.message}"


@dataclass
class AuditReport:
    issues: List[AuditIssue] = field(default_factory=list)

    def add_issue(self, key: str, severity: str, message: str) -> None:
        self.issues.append(AuditIssue(key=key, severity=severity, message=message))

    def is_clean(self) -> bool:
        return len(self.issues) == 0

    def by_severity(self, severity: str) -> List[AuditIssue]:
        return [i for i in self.issues if i.severity == severity]

    def summary(self) -> str:
        if self.is_clean():
            return "No audit issues found."
        high = len(self.by_severity("high"))
        medium = len(self.by_severity("medium"))
        low = len(self.by_severity("low"))
        return f"{len(self.issues)} issue(s): {high} high, {medium} medium, {low} low"


def _is_secret_key(key: str) -> bool:
    return any(p.search(key) for p in SECRET_PATTERNS)


def _is_weak_value(value: str) -> bool:
    return any(p.match(value) for p in WEAK_VALUE_PATTERNS)


def audit_env(env: Dict[str, str], check_weak_values: bool = True) -> AuditReport:
    """Audit an environment dict for security and quality issues."""
    report = AuditReport()

    for key, value in env.items():
        if not key.strip():
            report.add_issue(key, "low", "Key is blank or whitespace-only.")
            continue

        if key != key.upper():
            report.add_issue(key, "low", "Key is not uppercase; convention suggests ALL_CAPS.")

        if _is_secret_key(key) and not value:
            report.add_issue(key, "high", "Secret-like key has an empty value.")

        if check_weak_values and _is_secret_key(key) and value and _is_weak_value(value):
            report.add_issue(key, "high", f"Secret-like key has a weak/placeholder value: '{value}'.")

        if " " in key:
            report.add_issue(key, "medium", "Key contains spaces, which may cause parsing issues.")

    return report
