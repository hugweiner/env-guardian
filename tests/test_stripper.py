"""Tests for env_guardian.stripper."""
import pytest
from env_guardian.stripper import strip_env


@pytest.fixture()
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PASSWORD": "secret",
        "REDIS_URL": "redis://localhost",
        "APP_NAME": "myapp",
        "API_SECRET": "topsecret",
        "DEBUG": "true",
    }


def test_strip_returns_report(mixed_env):
    report = strip_env(mixed_env)
    assert report is not None


def test_no_rules_keeps_all_keys(mixed_env):
    report = strip_env(mixed_env)
    assert report.stripped_count == 0
    assert set(report.kept.keys()) == set(mixed_env.keys())


def test_exact_match_removes_key(mixed_env):
    report = strip_env(mixed_env, exact=["DEBUG"])
    assert "DEBUG" not in report.kept
    assert any(e.key == "DEBUG" for e in report.stripped)


def test_exact_match_reason_is_exact(mixed_env):
    report = strip_env(mixed_env, exact=["DEBUG"])
    entry = next(e for e in report.stripped if e.key == "DEBUG")
    assert entry.reason == "exact"


def test_glob_pattern_removes_matching_keys(mixed_env):
    report = strip_env(mixed_env, patterns=["DB_*"])
    assert "DB_HOST" not in report.kept
    assert "DB_PASSWORD" not in report.kept


def test_glob_pattern_keeps_non_matching_keys(mixed_env):
    report = strip_env(mixed_env, patterns=["DB_*"])
    assert "APP_NAME" in report.kept
    assert "DEBUG" in report.kept


def test_glob_pattern_reason_is_pattern(mixed_env):
    report = strip_env(mixed_env, patterns=["DB_*"])
    for entry in report.stripped:
        assert entry.reason == "pattern"


def test_suffix_pattern_matches_correctly(mixed_env):
    report = strip_env(mixed_env, patterns=["*_SECRET"])
    keys_stripped = {e.key for e in report.stripped}
    assert "API_SECRET" in keys_stripped
    assert "DB_HOST" not in keys_stripped


def test_stripped_entry_carries_value(mixed_env):
    report = strip_env(mixed_env, exact=["APP_NAME"])
    entry = next(e for e in report.stripped if e.key == "APP_NAME")
    assert entry.value == "myapp"


def test_stripped_entry_carries_pattern(mixed_env):
    report = strip_env(mixed_env, patterns=["DB_*"])
    for entry in report.stripped:
        assert entry.pattern == "DB_*"


def test_combined_exact_and_pattern(mixed_env):
    report = strip_env(mixed_env, patterns=["DB_*"], exact=["DEBUG"])
    keys_stripped = {e.key for e in report.stripped}
    assert "DB_HOST" in keys_stripped
    assert "DB_PASSWORD" in keys_stripped
    assert "DEBUG" in keys_stripped
    assert "APP_NAME" not in keys_stripped


def test_stripped_count_matches(mixed_env):
    report = strip_env(mixed_env, patterns=["DB_*"])
    assert report.stripped_count == 2


def test_is_clean_when_nothing_stripped(mixed_env):
    report = strip_env(mixed_env)
    assert report.is_clean is True


def test_is_not_clean_when_keys_stripped(mixed_env):
    report = strip_env(mixed_env, exact=["DEBUG"])
    assert report.is_clean is False


def test_summary_clean(mixed_env):
    report = strip_env(mixed_env)
    assert "No keys stripped" in report.summary()


def test_summary_with_stripped(mixed_env):
    report = strip_env(mixed_env, exact=["DEBUG", "APP_NAME"])
    assert "2" in report.summary()
