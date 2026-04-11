"""Tests for env_guardian.filterer."""
from __future__ import annotations

import pytest

from env_guardian.filterer import FilterReport, filter_env


@pytest.fixture()
def mixed_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_URL": "redis://localhost",
        "SECRET_KEY": "s3cr3t",
        "DEBUG": "true",
        "APP_ENV": "production",
    }


def test_filter_returns_report(mixed_env):
    report = filter_env(mixed_env)
    assert isinstance(report, FilterReport)


def test_no_rules_includes_all_keys(mixed_env):
    report = filter_env(mixed_env)
    assert report.matched_count() == len(mixed_env)
    assert report.excluded_count() == 0


def test_prefix_filter_includes_matching_keys(mixed_env):
    report = filter_env(mixed_env, prefixes=["DB_"])
    keys = {e.key for e in report.entries}
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "REDIS_URL" not in keys


def test_prefix_filter_excludes_non_matching_keys(mixed_env):
    report = filter_env(mixed_env, prefixes=["DB_"])
    assert report.excluded_count() == len(mixed_env) - 2


def test_pattern_filter_matches_regex(mixed_env):
    report = filter_env(mixed_env, patterns=[r"^(DB|REDIS)"])
    keys = {e.key for e in report.entries}
    assert "DB_HOST" in keys
    assert "REDIS_URL" in keys
    assert "SECRET_KEY" not in keys


def test_exclude_prefix_removes_keys(mixed_env):
    report = filter_env(mixed_env, exclude_prefixes=["DB_"])
    keys = {e.key for e in report.entries}
    assert "DB_HOST" not in keys
    assert "DB_PORT" not in keys
    assert "REDIS_URL" in keys


def test_exclude_pattern_removes_keys(mixed_env):
    report = filter_env(mixed_env, exclude_patterns=[r"SECRET"])
    keys = {e.key for e in report.entries}
    assert "SECRET_KEY" not in keys
    assert "DB_HOST" in keys


def test_exclude_takes_priority_over_include(mixed_env):
    # DB_ prefix included but also excluded — exclusion wins
    report = filter_env(mixed_env, prefixes=["DB_"], exclude_prefixes=["DB_"])
    assert report.matched_count() == 0


def test_matched_rule_set_for_prefix(mixed_env):
    report = filter_env(mixed_env, prefixes=["DB_"])
    for entry in report.entries:
        assert entry.matched_rule == "prefix:DB_"


def test_matched_rule_set_for_pattern(mixed_env):
    report = filter_env(mixed_env, patterns=[r"URL"])
    assert any(e.matched_rule == "pattern:URL" for e in report.entries)


def test_to_env_returns_dict(mixed_env):
    report = filter_env(mixed_env, prefixes=["DB_"])
    env = report.to_env()
    assert env == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_summary_string(mixed_env):
    report = filter_env(mixed_env, prefixes=["DB_"])
    s = report.summary()
    assert "matched" in s
    assert "excluded" in s
