"""Scores an environment's overall health based on audit, lint, and profile data."""

from dataclasses import dataclass, field
from typing import List

from env_guardian.auditor import AuditReport
from env_guardian.linter import LintReport

SEVERITY_WEIGHTS = {
    "high": 10,
    "medium": 5,
    "low": 2,
    "info": 1,
}

LEVEL_WEIGHTS = {
    "error": 8,
    "warning": 4,
    "info": 1,
}

MAX_SCORE = 100


@dataclass
class ScoreBreakdown:
    audit_penalty: int
    lint_penalty: int
    raw_score: int
    final_score: int
    grade: str

    def __str__(self) -> str:
        return (
            f"Score: {self.final_score}/100 (Grade: {self.grade}) "
            f"[audit_penalty={self.audit_penalty}, lint_penalty={self.lint_penalty}]"
        )


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _audit_penalty(report: AuditReport) -> int:
    total = 0
    for issue in report.issues:
        total += SEVERITY_WEIGHTS.get(issue.severity, 1)
    return total


def _lint_penalty(report: LintReport) -> int:
    total = 0
    for warning in report.warnings:
        total += LEVEL_WEIGHTS.get(warning.level, 1)
    return total


def score_env(audit_report: AuditReport, lint_report: LintReport) -> ScoreBreakdown:
    """Compute a health score (0-100) for an environment."""
    ap = _audit_penalty(audit_report)
    lp = _lint_penalty(lint_report)
    raw = MAX_SCORE - ap - lp
    final = max(0, min(MAX_SCORE, raw))
    return ScoreBreakdown(
        audit_penalty=ap,
        lint_penalty=lp,
        raw_score=raw,
        final_score=final,
        grade=_grade(final),
    )
