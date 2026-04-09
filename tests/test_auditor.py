"""Tests for env_guardian.auditor module."""

import pytest
from env_guardian.auditor import audit_env, AuditReport, AuditIssue


def test_clean_env_produces_no_issues():
    env = {"DATABASE_URL": "postgres://localhost/db", "PORT": "8080"}
    report = audit_env(env)
    assert report.is_clean()


def test_lowercase_key_flagged_as_low():
    report = audit_env({"database_url": "postgres://localhost/db"})
    issues = report.by_severity("low")
    assert any(i.key == "database_url" for i in issues)


def test_secret_key_with_empty_value_is_high():
    report = audit_env({"API_KEY": ""})
    high = report.by_severity("high")
    assert any(i.key == "API_KEY" for i in high)


def test_secret_key_with_weak_value_is_high():
    report = audit_env({"DB_PASSWORD": "password"})
    high = report.by_severity("high")
    assert any("weak" in i.message.lower() for i in high)


def test_secret_key_with_strong_value_passes():
    report = audit_env({"DB_PASSWORD": "xK9#mP2!qR7"})
    assert report.is_clean()


def test_key_with_spaces_is_medium():
    report = audit_env({"MY KEY": "value"})
    medium = report.by_severity("medium")
    assert any("spaces" in i.message.lower() for i in medium)


def test_check_weak_values_disabled_skips_weak_check():
    report = audit_env({"SECRET": "changeme"}, check_weak_values=False)
    high = report.by_severity("high")
    assert not any("weak" in i.message.lower() for i in high)


def test_summary_reports_counts():
    report = audit_env({"api_key": "", "MY KEY": "value"})
    summary = report.summary()
    assert "issue" in summary.lower()
    assert "high" in summary.lower()


def test_summary_clean():
    report = AuditReport()
    assert report.summary() == "No audit issues found."


def test_audit_issue_str():
    issue = AuditIssue(key="SECRET", severity="high", message="Empty value.")
    assert "[HIGH]" in str(issue)
    assert "SECRET" in str(issue)


def test_multiple_issues_accumulated():
    env = {
        "api_key": "secret",   # lowercase + weak value
        "MY KEY": "value",     # space in key
        "TOKEN": "",           # empty secret
    }
    report = audit_env(env)
    assert len(report.issues) >= 3


def test_by_severity_filters_correctly():
    report = AuditReport()
    report.add_issue("A", "high", "msg")
    report.add_issue("B", "low", "msg")
    report.add_issue("C", "high", "msg")
    assert len(report.by_severity("high")) == 2
    assert len(report.by_severity("low")) == 1
    assert len(report.by_severity("medium")) == 0
