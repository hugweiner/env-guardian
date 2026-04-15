"""Tests for env_guardian.splitter."""
import pytest

from env_guardian.splitter import split_env


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_HOST": "127.0.0.1",
        "REDIS_PORT": "6379",
        "APP_NAME": "guardian",
        "DEBUG": "true",
    }


def test_split_returns_report(mixed_env):
    report = split_env(mixed_env)
    assert report is not None


def test_db_keys_in_db_bucket(mixed_env):
    report = split_env(mixed_env, rules={"db": "DB_", "redis": "REDIS_"})
    db_keys = {e.key for e in report.by_bucket("db")}
    assert db_keys == {"DB_HOST", "DB_PORT"}


def test_redis_keys_in_redis_bucket(mixed_env):
    report = split_env(mixed_env, rules={"db": "DB_", "redis": "REDIS_"})
    redis_keys = {e.key for e in report.by_bucket("redis")}
    assert redis_keys == {"REDIS_HOST", "REDIS_PORT"}


def test_unmatched_keys_go_to_ungrouped(mixed_env):
    report = split_env(mixed_env, rules={"db": "DB_", "redis": "REDIS_"})
    ungrouped_keys = {e.key for e in report.by_bucket("ungrouped")}
    assert ungrouped_keys == {"APP_NAME", "DEBUG"}


def test_no_rules_puts_all_in_ungrouped(mixed_env):
    report = split_env(mixed_env)
    assert report.bucket_names() == ["ungrouped"]
    assert len(report.by_bucket("ungrouped")) == len(mixed_env)


def test_bucket_env_returns_dict(mixed_env):
    report = split_env(mixed_env, rules={"db": "DB_"})
    env = report.bucket_env("db")
    assert env == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_bucket_names_contains_expected_buckets(mixed_env):
    report = split_env(mixed_env, rules={"db": "DB_", "redis": "REDIS_"})
    names = set(report.bucket_names())
    assert "db" in names
    assert "redis" in names
    assert "ungrouped" in names


def test_summary_mentions_bucket_count(mixed_env):
    report = split_env(mixed_env, rules={"db": "DB_", "redis": "REDIS_"})
    assert "3 bucket" in report.summary()


def test_summary_mentions_total_keys(mixed_env):
    report = split_env(mixed_env, rules={"db": "DB_"})
    assert str(len(mixed_env)) in report.summary()


def test_all_entries_length_matches_env(mixed_env):
    report = split_env(mixed_env, rules={"db": "DB_"})
    assert len(report.all_entries()) == len(mixed_env)
