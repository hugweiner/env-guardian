"""Tests for env_guardian.rewriter."""
import pytest
from env_guardian.rewriter import rewrite_env, RewriteReport


@pytest.fixture()
def base_env():
    return {
        "db_host": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET_KEY": "s3cr3t!",
        "REDIS_URL": "redis://localhost:6379",
    }


def test_rewrite_returns_report(base_env):
    report = rewrite_env(base_env)
    assert isinstance(report, RewriteReport)


def test_no_rules_produces_no_rewrites(base_env):
    report = rewrite_env(base_env)
    assert report.is_clean()
    assert report.rewritten_count == 0


def test_no_rules_preserves_all_keys(base_env):
    report = rewrite_env(base_env)
    assert set(report.result_env.keys()) == set(base_env.keys())


def test_no_rules_preserves_all_values(base_env):
    report = rewrite_env(base_env)
    assert report.result_env == base_env


def test_key_rule_uppercases_lowercase_key():
    env = {"db_host": "localhost"}
    report = rewrite_env(env, key_rules=[(r"[a-z]", lambda m: m.group().upper())])
    assert "DB_HOST" in report.result_env


def test_key_rule_marks_entry_as_rewritten():
    env = {"db_host": "localhost"}
    report = rewrite_env(env, key_rules=[(r"db_", "database_")])
    entry = report.entries[0]
    assert entry.key_rewritten is True
    assert entry.original_key == "db_host"
    assert entry.key == "database_host"


def test_value_rule_replaces_localhost():
    env = {"DB_HOST": "localhost"}
    report = rewrite_env(env, value_rules=[(r"localhost", "127.0.0.1")])
    assert report.result_env["DB_HOST"] == "127.0.0.1"


def test_value_rule_marks_entry_as_rewritten():
    env = {"DB_HOST": "localhost"}
    report = rewrite_env(env, value_rules=[(r"localhost", "127.0.0.1")])
    entry = report.entries[0]
    assert entry.value_rewritten is True
    assert entry.original_value == "localhost"


def test_unchanged_entry_not_flagged(base_env):
    report = rewrite_env(base_env, key_rules=[(r"NONEXISTENT", "X")])
    for entry in report.entries:
        assert entry.key_rewritten is False


def test_rewritten_count_correct(base_env):
    # Only keys containing lowercase letters will change
    report = rewrite_env(base_env, key_rules=[(r"db_", "DB_")])
    assert report.rewritten_count == 1


def test_multiple_key_rules_applied_in_order():
    env = {"app_secret": "value"}
    report = rewrite_env(
        env,
        key_rules=[(r"app_", "APP_"), (r"secret", "SECRET")],
    )
    assert "APP_SECRET" in report.result_env


def test_summary_reflects_rewritten_count(base_env):
    report = rewrite_env(base_env, key_rules=[(r"db_", "DB_")])
    summary = report.summary()
    assert "1/" in summary
    assert "rewritten" in summary


def test_all_entries_present_in_result_env(base_env):
    report = rewrite_env(base_env, key_rules=[(r"db_", "DB_")])
    assert len(report.result_env) == len(base_env)
