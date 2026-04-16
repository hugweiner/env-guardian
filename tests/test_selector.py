"""Tests for env_guardian.selector."""
import pytest
from env_guardian.selector import select_env


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_URL": "redis://localhost",
        "APP_SECRET": "s3cr3t",
        "APP_DEBUG": "true",
        "LOG_LEVEL": "info",
    }


def test_select_returns_report(mixed_env):
    report = select_env(mixed_env)
    assert report is not None


def test_no_criteria_selects_all(mixed_env):
    report = select_env(mixed_env)
    assert report.selected_count == len(mixed_env)


def test_no_criteria_reason_is_all(mixed_env):
    report = select_env(mixed_env)
    for entry in report.entries:
        assert entry.reason == "all"


def test_key_filter_selects_exact_keys(mixed_env):
    report = select_env(mixed_env, keys=["DB_HOST", "LOG_LEVEL"])
    assert set(report.keys()) == {"DB_HOST", "LOG_LEVEL"}


def test_key_filter_excludes_other_keys(mixed_env):
    report = select_env(mixed_env, keys=["DB_HOST"])
    assert "REDIS_URL" not in report.keys()


def test_prefix_filter_selects_matching_keys(mixed_env):
    report = select_env(mixed_env, prefix="DB_")
    assert set(report.keys()) == {"DB_HOST", "DB_PORT"}


def test_suffix_filter_selects_matching_keys(mixed_env):
    report = select_env(mixed_env, suffix="_URL")
    assert "REDIS_URL" in report.keys()
    assert "DB_HOST" not in report.keys()


def test_contains_filter_selects_matching_keys(mixed_env):
    report = select_env(mixed_env, contains="SECRET")
    assert "APP_SECRET" in report.keys()
    assert "DB_HOST" not in report.keys()


def test_multiple_criteria_are_or_combined(mixed_env):
    report = select_env(mixed_env, prefix="DB_", contains="SECRET")
    assert "DB_HOST" in report.keys()
    assert "APP_SECRET" in report.keys()
    assert "LOG_LEVEL" not in report.keys()


def test_selected_env_contains_correct_values(mixed_env):
    report = select_env(mixed_env, keys=["DB_HOST"])
    assert report.selected_env["DB_HOST"] == "localhost"


def test_summary_shows_count(mixed_env):
    report = select_env(mixed_env, prefix="APP_")
    assert "2" in report.summary()


def test_no_match_returns_empty_report(mixed_env):
    report = select_env(mixed_env, prefix="NOPE_")
    assert report.selected_count == 0
    assert report.selected_env == {}
