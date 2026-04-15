"""Tests for env_guardian.duplicator."""
import pytest
from env_guardian.duplicator import duplicate_env, DuplicateReport


@pytest.fixture()
def base_env() -> dict:
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "REDIS_URL": "redis://localhost:6379",
        "SECRET_KEY": "s3cr3t",
    }


def test_duplicate_returns_report(base_env):
    report = duplicate_env(base_env, {"DATABASE_URL": "DB_URL_COPY"})
    assert isinstance(report, DuplicateReport)


def test_single_key_duplicated(base_env):
    report = duplicate_env(base_env, {"DATABASE_URL": "DB_URL_COPY"})
    assert report.duplicated_count() == 1


def test_duplicated_entry_carries_correct_value(base_env):
    report = duplicate_env(base_env, {"DATABASE_URL": "DB_URL_COPY"})
    entry = report.entries[0]
    assert entry.value == "postgres://localhost/db"
    assert not entry.skipped


def test_multiple_keys_duplicated(base_env):
    mapping = {"DATABASE_URL": "DB_COPY", "REDIS_URL": "REDIS_COPY"}
    report = duplicate_env(base_env, mapping)
    assert report.duplicated_count() == 2


def test_result_env_contains_new_keys(base_env):
    report = duplicate_env(base_env, {"SECRET_KEY": "SECRET_KEY_BACKUP"})
    result = report.result_env(base_env)
    assert "SECRET_KEY_BACKUP" in result
    assert result["SECRET_KEY_BACKUP"] == "s3cr3t"


def test_result_env_preserves_original_keys(base_env):
    report = duplicate_env(base_env, {"SECRET_KEY": "SECRET_KEY_BACKUP"})
    result = report.result_env(base_env)
    assert "SECRET_KEY" in result


def test_missing_source_key_is_skipped(base_env):
    report = duplicate_env(base_env, {"NONEXISTENT": "COPY"})
    assert report.skipped_count() == 1
    assert report.duplicated_count() == 0


def test_missing_source_key_skip_reason(base_env):
    report = duplicate_env(base_env, {"NONEXISTENT": "COPY"})
    assert report.entries[0].skip_reason == "source key not found"


def test_no_overwrite_skips_existing_target(base_env):
    env = {**base_env, "REDIS_COPY": "already_here"}
    report = duplicate_env(env, {"REDIS_URL": "REDIS_COPY"}, overwrite=False)
    assert report.skipped_count() == 1
    assert report.entries[0].skip_reason == "target key already exists"


def test_overwrite_true_replaces_existing_target(base_env):
    env = {**base_env, "REDIS_COPY": "already_here"}
    report = duplicate_env(env, {"REDIS_URL": "REDIS_COPY"}, overwrite=True)
    assert report.duplicated_count() == 1
    result = report.result_env(env)
    assert result["REDIS_COPY"] == "redis://localhost:6379"


def test_skipped_key_not_in_result_env(base_env):
    report = duplicate_env(base_env, {"NONEXISTENT": "COPY"})
    result = report.result_env(base_env)
    assert "COPY" not in result


def test_empty_mapping_produces_empty_report(base_env):
    report = duplicate_env(base_env, {})
    assert report.duplicated_count() == 0
    assert report.skipped_count() == 0
    assert report.entries == []


def test_summary_string(base_env):
    report = duplicate_env(
        base_env,
        {"DATABASE_URL": "DB_COPY", "NONEXISTENT": "SKIP_COPY"},
    )
    summary = report.summary()
    assert "1 key(s) duplicated" in summary
    assert "1 skipped" in summary
