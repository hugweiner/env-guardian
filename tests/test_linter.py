"""Tests for env_guardian.linter module."""

import pytest
from env_guardian.linter import lint_env, LintReport, LintWarning


def test_clean_env_produces_no_warnings():
    env = {"DATABASE_URL": "postgres://host/db", "SECRET_KEY": "supersecret"}
    report = lint_env(env)
    assert report.is_clean
    assert report.summary() == "No lint issues found."


def test_lowercase_key_flagged():
    report = lint_env({"my_var": "value"})
    assert not report.is_clean
    keys = [w.key for w in report.warnings]
    assert "my_var" in keys


def test_lowercase_key_is_error_in_strict_mode():
    report = lint_env({"bad_key": "value"}, strict=True)
    errors = report.by_severity('error')
    assert any(w.key == "bad_key" for w in errors)


def test_lowercase_key_is_warning_in_normal_mode():
    report = lint_env({"bad_key": "value"}, strict=False)
    warnings = report.by_severity('warning')
    assert any(w.key == "bad_key" for w in warnings)


def test_double_underscore_flagged_as_info():
    report = lint_env({"MY__VAR": "value"})
    infos = report.by_severity('info')
    assert any(w.key == "MY__VAR" for w in infos)


def test_value_with_leading_whitespace_flagged():
    report = lint_env({"MY_VAR": "  value"})
    assert not report.is_clean
    assert any("whitespace" in w.message for w in report.warnings)


def test_value_with_trailing_whitespace_flagged():
    report = lint_env({"MY_VAR": "value  "})
    assert not report.is_clean
    assert any("whitespace" in w.message for w in report.warnings)


def test_placeholder_value_flagged():
    for placeholder in ["<your-value>", "${MY_VAR}", "CHANGE_ME", "TODO"]:
        report = lint_env({"API_KEY": placeholder})
        assert not report.is_clean, f"Expected warning for placeholder: {placeholder}"
        assert any("placeholder" in w.message.lower() for w in report.warnings)


def test_localhost_in_non_dev_key_flagged_as_info():
    report = lint_env({"DATABASE_URL": "http://localhost:5432/db"})
    infos = report.by_severity('info')
    assert any("localhost" in w.message.lower() for w in infos)


def test_localhost_in_dev_key_not_flagged():
    report = lint_env({"DEV_DATABASE_URL": "http://localhost:5432/db"})
    localhost_issues = [w for w in report.warnings if "localhost" in w.message.lower()]
    assert len(localhost_issues) == 0


def test_very_long_value_flagged_as_info():
    report = lint_env({"BIG_VAR": "x" * 3000})
    infos = report.by_severity('info')
    assert any("unusually long" in w.message for w in infos)


def test_summary_counts_severities():
    env = {
        "bad_key": "  value  ",   # warning (naming) + warning (whitespace)
        "MY__VAR": "value",        # info (double underscore)
    }
    report = lint_env(env)
    summary = report.summary()
    assert "warning" in summary
    assert "info" in summary


def test_lint_warning_str():
    w = LintWarning(key="MY_KEY", message="Some issue", severity="warning")
    assert str(w) == "[WARNING] MY_KEY: Some issue"
