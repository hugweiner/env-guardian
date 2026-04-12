"""Tests for env_guardian.extractor."""
import pytest
from env_guardian.extractor import extract_env, ExtractReport


@pytest.fixture()
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_HOST": "redis",
        "SECRET_KEY": "s3cr3t",
        "APP_ENV": "production",
        "APP_DEBUG": "false",
    }


def test_extract_returns_report(mixed_env):
    report = extract_env(mixed_env)
    assert isinstance(report, ExtractReport)


def test_no_filters_extracts_all_keys(mixed_env):
    report = extract_env(mixed_env)
    assert report.extracted_count() == len(mixed_env)


def test_exact_key_extracted(mixed_env):
    report = extract_env(mixed_env, keys=["SECRET_KEY"])
    env = report.extracted_env()
    assert "SECRET_KEY" in env
    assert env["SECRET_KEY"] == "s3cr3t"


def test_exact_key_excludes_others(mixed_env):
    report = extract_env(mixed_env, keys=["SECRET_KEY"])
    assert report.extracted_count() == 1


def test_missing_exact_key_not_in_report(mixed_env):
    report = extract_env(mixed_env, keys=["NONEXISTENT"])
    assert report.extracted_count() == 0


def test_pattern_filter_matches_wildcard(mixed_env):
    report = extract_env(mixed_env, patterns=["DB_*"])
    env = report.extracted_env()
    assert "DB_HOST" in env
    assert "DB_PORT" in env
    assert "REDIS_HOST" not in env


def test_pattern_filter_match_type_is_pattern(mixed_env):
    report = extract_env(mixed_env, patterns=["DB_*"])
    for entry in report.entries:
        assert entry.matched_by == "pattern"


def test_prefix_filter_matches_prefix(mixed_env):
    report = extract_env(mixed_env, prefix="APP_")
    env = report.extracted_env()
    assert "APP_ENV" in env
    assert "APP_DEBUG" in env
    assert "DB_HOST" not in env


def test_prefix_filter_match_type_is_prefix(mixed_env):
    report = extract_env(mixed_env, prefix="APP_")
    for entry in report.entries:
        assert entry.matched_by == "prefix"


def test_exact_key_takes_priority_over_pattern(mixed_env):
    report = extract_env(mixed_env, keys=["DB_HOST"], patterns=["DB_*"])
    db_host_entry = next(e for e in report.entries if e.key == "DB_HOST")
    assert db_host_entry.matched_by == "exact"


def test_by_match_type_filters_correctly(mixed_env):
    report = extract_env(mixed_env, keys=["SECRET_KEY"], patterns=["APP_*"])
    exact = report.by_match_type("exact")
    pattern = report.by_match_type("pattern")
    assert len(exact) == 1
    assert exact[0].key == "SECRET_KEY"
    assert all(e.key.startswith("APP_") for e in pattern)


def test_summary_contains_count(mixed_env):
    report = extract_env(mixed_env, prefix="DB_")
    assert "2" in report.summary()


def test_extracted_env_returns_dict(mixed_env):
    report = extract_env(mixed_env, keys=["DB_HOST", "DB_PORT"])
    result = report.extracted_env()
    assert isinstance(result, dict)
    assert result == {"DB_HOST": "localhost", "DB_PORT": "5432"}
