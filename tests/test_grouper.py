"""Tests for env_guardian.grouper."""
import pytest

from env_guardian.grouper import GroupEntry, group_env


@pytest.fixture()
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "REDIS_HOST": "redis",
        "REDIS_PORT": "6379",
        "DEBUG": "true",
        "SECRET_KEY": "abc123",
    }


def test_group_env_returns_report(mixed_env):
    report = group_env(mixed_env)
    assert report is not None


def test_db_keys_grouped_together(mixed_env):
    report = group_env(mixed_env)
    assert "DB" in report.group_names()
    keys = [e.key for e in report.by_group("DB")]
    assert set(keys) == {"DB_HOST", "DB_PORT", "DB_NAME"}


def test_redis_keys_grouped_together(mixed_env):
    report = group_env(mixed_env)
    assert "REDIS" in report.group_names()
    keys = [e.key for e in report.by_group("REDIS")]
    assert set(keys) == {"REDIS_HOST", "REDIS_PORT"}


def test_singleton_prefix_becomes_ungrouped(mixed_env):
    # SECRET_KEY is the only SECRET_* key — with default min_group_size=2 it is ungrouped
    report = group_env(mixed_env, min_group_size=2)
    ungrouped_keys = [e.key for e in report.ungrouped]
    assert "SECRET_KEY" in ungrouped_keys


def test_keyless_prefix_key_is_ungrouped(mixed_env):
    # DEBUG has no underscore, so it should be ungrouped
    report = group_env(mixed_env)
    ungrouped_keys = [e.key for e in report.ungrouped]
    assert "DEBUG" in ungrouped_keys


def test_group_count(mixed_env):
    report = group_env(mixed_env, min_group_size=2)
    assert report.group_count() == 2  # DB, REDIS


def test_total_keys_matches_input(mixed_env):
    report = group_env(mixed_env)
    assert report.total_keys() == len(mixed_env)


def test_summary_contains_group_count(mixed_env):
    report = group_env(mixed_env, min_group_size=2)
    assert "2 group" in report.summary()


def test_custom_separator():
    env = {"APP.HOST": "localhost", "APP.PORT": "8080", "STANDALONE": "yes"}
    report = group_env(env, separator=".", min_group_size=2)
    assert "APP" in report.group_names()
    assert len(report.by_group("APP")) == 2


def test_min_group_size_one_groups_singletons():
    env = {"FOO_BAR": "1", "BAZ_QUX": "2"}
    report = group_env(env, min_group_size=1)
    # Both should be grouped since each prefix has >=1 member
    assert len(report.ungrouped) == 0


def test_entry_suffix_set_correctly():
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    report = group_env(env, min_group_size=2)
    suffixes = {e.suffix for e in report.by_group("DB")}
    assert suffixes == {"HOST", "PORT"}


def test_empty_env_produces_empty_report():
    report = group_env({})
    assert report.group_count() == 0
    assert report.total_keys() == 0
    assert report.ungrouped == []
