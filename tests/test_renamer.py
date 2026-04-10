"""Tests for env_guardian.renamer."""

import pytest

from env_guardian.renamer import rename_keys


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
        "DEBUG": "true",
    }


def test_rename_single_key(base_env):
    report = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert "DATABASE_HOST" in report.result_env
    assert "DB_HOST" not in report.result_env
    assert report.result_env["DATABASE_HOST"] == "localhost"


def test_renamed_count(base_env):
    report = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
    assert report.renamed_count() == 2


def test_missing_source_key_is_skipped(base_env):
    report = rename_keys(base_env, {"MISSING_KEY": "NEW_KEY"})
    assert report.skipped_count() == 1
    assert "NEW_KEY" not in report.result_env


def test_missing_source_key_skip_reason(base_env):
    report = rename_keys(base_env, {"MISSING_KEY": "NEW_KEY"})
    entry = report.entries[0]
    assert entry.skipped is True
    assert "not found" in entry.skip_reason


def test_existing_target_key_skipped_without_overwrite(base_env):
    # DB_PORT already exists; renaming DEBUG -> DB_PORT should be skipped
    report = rename_keys(base_env, {"DEBUG": "DB_PORT"}, overwrite=False)
    assert report.skipped_count() == 1
    assert report.result_env["DB_PORT"] == "5432"  # unchanged
    assert report.result_env["DEBUG"] == "true"    # original preserved


def test_existing_target_key_overwritten_with_flag(base_env):
    report = rename_keys(base_env, {"DEBUG": "DB_PORT"}, overwrite=True)
    assert report.result_env["DB_PORT"] == "true"
    assert "DEBUG" not in report.result_env
    assert report.renamed_count() == 1


def test_unrelated_keys_preserved(base_env):
    report = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    assert report.result_env["DB_PORT"] == "5432"
    assert report.result_env["APP_SECRET"] == "s3cr3t"
    assert report.result_env["DEBUG"] == "true"


def test_empty_mapping_returns_original_env(base_env):
    report = rename_keys(base_env, {})
    assert report.result_env == base_env
    assert report.renamed_count() == 0
    assert report.is_clean()


def test_empty_env_with_mapping():
    report = rename_keys({}, {"SOME_KEY": "OTHER_KEY"})
    assert report.result_env == {}
    assert report.skipped_count() == 1


def test_summary_string(base_env):
    report = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST", "MISSING": "X"})
    summary = report.summary()
    assert "1" in summary  # 1 renamed
    assert "1" in summary  # 1 skipped


def test_str_representation_of_entry(base_env):
    report = rename_keys(base_env, {"DB_HOST": "DATABASE_HOST"})
    entry = report.entries[0]
    text = str(entry)
    assert "DB_HOST" in text
    assert "DATABASE_HOST" in text


def test_str_representation_of_skipped_entry(base_env):
    report = rename_keys(base_env, {"MISSING": "NEW"})
    entry = report.entries[0]
    text = str(entry)
    assert "SKIP" in text
