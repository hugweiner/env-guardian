"""Tests for env_guardian.aliaser."""
import pytest
from env_guardian.aliaser import alias_env, AliasReport


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
        "DEBUG": "true",
    }


def test_alias_single_key(base_env):
    report = alias_env(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert any(e.alias_key == "DATABASE_HOST" and not e.skipped for e in report.entries)


def test_aliased_entry_carries_value(base_env):
    report = alias_env(base_env, {"DB_HOST": "DATABASE_HOST"})
    entry = next(e for e in report.entries if e.alias_key == "DATABASE_HOST")
    assert entry.value == "localhost"


def test_missing_source_key_is_skipped(base_env):
    report = alias_env(base_env, {"MISSING_KEY": "NEW_KEY"})
    entry = next(e for e in report.entries if e.original_key == "MISSING_KEY")
    assert entry.skipped is True


def test_missing_source_key_skip_reason(base_env):
    report = alias_env(base_env, {"MISSING_KEY": "NEW_KEY"})
    entry = next(e for e in report.entries if e.original_key == "MISSING_KEY")
    assert "not found" in entry.skip_reason


def test_aliased_count(base_env):
    report = alias_env(base_env, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert report.aliased_count() == 2


def test_skipped_count(base_env):
    report = alias_env(base_env, {"GHOST": "PHANTOM", "DB_HOST": "DATABASE_HOST"})
    assert report.skipped_count() == 1


def test_result_env_uses_alias_keys(base_env):
    report = alias_env(base_env, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    result = report.result_env()
    assert "DATABASE_HOST" in result
    assert "DATABASE_PORT" in result
    assert "DB_HOST" not in result


def test_result_env_excludes_skipped(base_env):
    report = alias_env(base_env, {"GHOST": "PHANTOM"})
    result = report.result_env()
    assert "PHANTOM" not in result


def test_keep_original_retains_unaliased_keys(base_env):
    report = alias_env(base_env, {"DB_HOST": "DATABASE_HOST"}, keep_original=True)
    result = report.result_env()
    assert "DATABASE_HOST" in result
    assert "DEBUG" in result


def test_summary_string(base_env):
    report = alias_env(base_env, {"DB_HOST": "DATABASE_HOST", "GHOST": "PHANTOM"})
    summary = report.summary()
    assert "1" in summary
    assert "aliased" in summary


def test_str_representation_of_entry(base_env):
    report = alias_env(base_env, {"DB_HOST": "DATABASE_HOST"})
    entry = next(e for e in report.entries if e.alias_key == "DATABASE_HOST")
    text = str(entry)
    assert "DB_HOST" in text
    assert "DATABASE_HOST" in text


def test_str_representation_of_skipped_entry(base_env):
    report = alias_env(base_env, {"GHOST": "PHANTOM"})
    entry = next(e for e in report.entries if e.original_key == "GHOST")
    text = str(entry)
    assert "SKIPPED" in text
