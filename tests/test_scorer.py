"""Tests for env_guardian.scorer and env_guardian.score_formatter."""

import json
import pytest

from env_guardian.auditor import AuditReport, AuditIssue
from env_guardian.linter import LintReport, LintWarning
from env_guardian.scorer import score_env, ScoreBreakdown, _grade
from env_guardian.score_formatter import format_text, format_json, format_csv


def _make_audit(*issues) -> AuditReport:
    r = AuditReport()
    for sev, key, msg in issues:
        r.add_issue(AuditIssue(key=key, severity=sev, message=msg))
    return r


def _make_lint(*warnings) -> LintReport:
    r = LintReport()
    for level, key, msg in warnings:
        r.add(LintWarning(key=key, level=level, message=msg))
    return r


def test_perfect_score_when_no_issues():
    audit = _make_audit()
    lint = _make_lint()
    result = score_env(audit, lint)
    assert result.final_score == 100
    assert result.grade == "A"
    assert result.audit_penalty == 0
    assert result.lint_penalty == 0


def test_audit_high_severity_reduces_score():
    audit = _make_audit(("high", "SECRET", "empty secret"))
    lint = _make_lint()
    result = score_env(audit, lint)
    assert result.audit_penalty == 10
    assert result.final_score == 90


def test_lint_error_reduces_score():
    audit = _make_audit()
    lint = _make_lint(("error", "bad_key", "lowercase key"))
    result = score_env(audit, lint)
    assert result.lint_penalty == 8
    assert result.final_score == 92


def test_combined_penalties_accumulate():
    audit = _make_audit(
        ("high", "SECRET", "weak"),
        ("medium", "DB_PASS", "medium issue"),
    )
    lint = _make_lint(
        ("warning", "bad_key", "lowercase"),
    )
    result = score_env(audit, lint)
    assert result.audit_penalty == 15  # 10 + 5
    assert result.lint_penalty == 4
    assert result.final_score == 81
    assert result.grade == "B"


def test_score_never_goes_below_zero():
    audit = _make_audit(*[("high", f"K{i}", "x") for i in range(15)])
    lint = _make_lint()
    result = score_env(audit, lint)
    assert result.final_score == 0


def test_grade_boundaries():
    assert _grade(100) == "A"
    assert _grade(90) == "A"
    assert _grade(89) == "B"
    assert _grade(75) == "B"
    assert _grade(74) == "C"
    assert _grade(60) == "C"
    assert _grade(59) == "D"
    assert _grade(40) == "D"
    assert _grade(39) == "F"
    assert _grade(0) == "F"


def test_str_representation():
    bd = ScoreBreakdown(audit_penalty=5, lint_penalty=3, raw_score=92, final_score=92, grade="A")
    s = str(bd)
    assert "92/100" in s
    assert "Grade: A" in s


def test_format_text_contains_score():
    audit = _make_audit()
    lint = _make_lint()
    result = score_env(audit, lint)
    text = format_text(result)
    assert "100" in text
    assert "Grade" in text


def test_format_json_is_valid():
    audit = _make_audit(("low", "X", "msg"))
    lint = _make_lint()
    result = score_env(audit, lint)
    data = json.loads(format_json(result))
    assert "final_score" in data
    assert "grade" in data
    assert data["audit_penalty"] == 2


def test_format_csv_contains_header():
    audit = _make_audit()
    lint = _make_lint()
    result = score_env(audit, lint)
    csv_out = format_csv(result)
    assert "metric" in csv_out
    assert "final_score" in csv_out
