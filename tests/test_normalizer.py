"""Tests for env_guardian.normalizer."""

import pytest
from env_guardian.normalizer import normalize_env, NormalizeReport, NormalizeWarning


def test_clean_env_produces_no_warnings():
    env = {"DATABASE_URL": "postgres://localhost", "PORT": "5432"}
    report = normalize_env(env)
    assert report.is_clean()
    assert report.warnings == []


def test_lowercase_key_is_uppercased():
    report = normalize_env({"database_url": "postgres://localhost"})
    assert "DATABASE_URL" in report.env
    assert "database_url" not in report.env


def test_lowercase_key_produces_warning():
    report = normalize_env({"my_key": "value"})
    assert not report.is_clean()
    keys_warned = [w.key for w in report.warnings]
    assert "MY_KEY" in keys_warned


def test_mixed_case_key_is_uppercased():
    report = normalize_env({"My_Key": "hello"})
    assert "MY_KEY" in report.env


def test_key_with_leading_whitespace_is_stripped():
    report = normalize_env({"  PORT": "8080"})
    assert "PORT" in report.env
    assert not any(k.startswith(" ") for k in report.env)


def test_value_with_trailing_whitespace_is_stripped():
    report = normalize_env({"HOST": "localhost   "})
    assert report.env["HOST"] == "localhost"


def test_value_whitespace_produces_warning():
    report = normalize_env({"HOST": "  localhost  "})
    value_warnings = [w for w in report.warnings if w.reason == "value whitespace stripped"]
    assert len(value_warnings) == 1
    assert value_warnings[0].normalized == "localhost"


def test_already_clean_value_no_warning():
    report = normalize_env({"HOST": "localhost"})
    assert report.is_clean()


def test_summary_clean():
    report = normalize_env({"KEY": "value"})
    assert "No normalization" in report.summary()


def test_summary_with_changes():
    report = normalize_env({"key": "value"})
    assert "1 normalization change" in report.summary()


def test_multiple_keys_normalized():
    env = {"db_host": "localhost", "db_port": "5432", "APP_NAME": "myapp"}
    report = normalize_env(env)
    assert "DB_HOST" in report.env
    assert "DB_PORT" in report.env
    assert "APP_NAME" in report.env
    assert len(report.warnings) == 2  # only the two lowercase keys


def test_normalize_warning_str():
    w = NormalizeWarning(
        key="MY_KEY",
        original="my_key",
        normalized="MY_KEY",
        reason="key normalized (uppercase/strip)",
    )
    result = str(w)
    assert "MY_KEY" in result
    assert "my_key" in result


def test_empty_env_returns_empty_report():
    report = normalize_env({})
    assert report.env == {}
    assert report.is_clean()
