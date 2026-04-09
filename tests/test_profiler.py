"""Tests for env_guardian.profiler."""

import pytest
from env_guardian.profiler import profile_env, ProfileReport, _classify


SAMPLE_ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "s3cr3t!",
    "DEBUG": "true",
    "PORT": "8080",
    "APP_NAME": "myapp",
    "EMPTY_VAR": "",
}


def test_profile_returns_report():
    report = profile_env(SAMPLE_ENV)
    assert isinstance(report, ProfileReport)
    assert report.total == len(SAMPLE_ENV)


def test_secret_classified_correctly():
    assert _classify("SECRET_KEY", "abc") == "secret"
    assert _classify("DB_PASSWORD", "abc") == "secret"
    assert _classify("API_TOKEN", "abc") == "secret"


def test_url_classified_correctly():
    assert _classify("DATABASE_URL", "postgres://") == "url"
    assert _classify("REDIS_HOST", "localhost") == "url"


def test_flag_classified_correctly():
    assert _classify("DEBUG", "true") == "flag"
    assert _classify("FEATURE_ENABLED", "1") == "flag"


def test_numeric_classified_correctly():
    assert _classify("PORT", "8080") == "numeric"
    assert _classify("TIMEOUT", "30") == "numeric"


def test_general_fallback():
    assert _classify("APP_NAME", "myapp") == "general"


def test_empty_count():
    report = profile_env(SAMPLE_ENV)
    assert report.empty_count == 1


def test_by_category_groups_correctly():
    report = profile_env(SAMPLE_ENV)
    cats = report.by_category
    assert "secret" in cats
    assert "url" in cats
    assert any(e.key == "SECRET_KEY" for e in cats["secret"])


def test_summary_contains_total():
    report = profile_env(SAMPLE_ENV)
    summary = report.summary()
    assert str(report.total) in summary
    assert "Empty" in summary


def test_empty_env_produces_empty_report():
    report = profile_env({})
    assert report.total == 0
    assert report.empty_count == 0
    assert report.by_category == {}


def test_profile_entry_str_shows_category():
    report = profile_env({"SECRET_KEY": "abc"})
    entry = report.entries[0]
    assert "secret" in str(entry)
    assert "SECRET_KEY" in str(entry)


def test_profile_entry_str_shows_empty():
    report = profile_env({"EMPTY_VAR": ""})
    entry = report.entries[0]
    assert "empty" in str(entry).lower()
