"""Tests for env_guardian.pruner."""
import pytest
from env_guardian.pruner import prune_env


@pytest.fixture()
def mixed_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "LEGACY_TOKEN": "abc123",
        "LEGACY_SECRET": "xyz",
        "TMP_FILE": "/tmp/foo",
        "APP_NAME": "guardian",
        "EMPTY_KEY": "",
        "WHITESPACE_KEY": "   ",
    }


def test_prune_returns_report(mixed_env):
    report = prune_env(mixed_env)
    assert report is not None


def test_no_patterns_no_remove_empty_keeps_all(mixed_env):
    report = prune_env(mixed_env)
    assert report.pruned_count == 0
    assert report.kept_count == len(mixed_env)


def test_pattern_prunes_matching_keys(mixed_env):
    report = prune_env(mixed_env, patterns=["LEGACY_*"])
    pruned_keys = {e.key for e in report.entries if e.pruned}
    assert "LEGACY_TOKEN" in pruned_keys
    assert "LEGACY_SECRET" in pruned_keys


def test_pattern_does_not_prune_non_matching_keys(mixed_env):
    report = prune_env(mixed_env, patterns=["LEGACY_*"])
    kept_keys = {e.key for e in report.entries if not e.pruned}
    assert "DATABASE_URL" in kept_keys
    assert "APP_NAME" in kept_keys


def test_multiple_patterns_applied(mixed_env):
    report = prune_env(mixed_env, patterns=["LEGACY_*", "TMP_*"])
    pruned_keys = {e.key for e in report.entries if e.pruned}
    assert "TMP_FILE" in pruned_keys
    assert "LEGACY_TOKEN" in pruned_keys


def test_remove_empty_prunes_empty_value(mixed_env):
    report = prune_env(mixed_env, remove_empty=True)
    pruned_keys = {e.key for e in report.entries if e.pruned}
    assert "EMPTY_KEY" in pruned_keys


def test_remove_empty_prunes_whitespace_value(mixed_env):
    report = prune_env(mixed_env, remove_empty=True)
    pruned_keys = {e.key for e in report.entries if e.pruned}
    assert "WHITESPACE_KEY" in pruned_keys


def test_remove_empty_false_keeps_empty_values(mixed_env):
    report = prune_env(mixed_env, remove_empty=False)
    kept_keys = {e.key for e in report.entries if not e.pruned}
    assert "EMPTY_KEY" in kept_keys


def test_pruned_env_excludes_pruned_keys(mixed_env):
    report = prune_env(mixed_env, patterns=["LEGACY_*"])
    result = report.pruned_env
    assert "LEGACY_TOKEN" not in result
    assert "LEGACY_SECRET" not in result
    assert "DATABASE_URL" in result


def test_is_clean_when_nothing_pruned(mixed_env):
    report = prune_env(mixed_env)
    assert report.is_clean


def test_is_not_clean_when_something_pruned(mixed_env):
    report = prune_env(mixed_env, patterns=["LEGACY_*"])
    assert not report.is_clean


def test_reason_contains_pattern(mixed_env):
    report = prune_env(mixed_env, patterns=["LEGACY_*"])
    entry = next(e for e in report.entries if e.key == "LEGACY_TOKEN")
    assert "LEGACY_*" in entry.reason


def test_summary_string(mixed_env):
    report = prune_env(mixed_env, patterns=["LEGACY_*"])
    s = report.summary()
    assert "pruned" in s
    assert "kept" in s
