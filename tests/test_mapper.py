"""Tests for env_guardian.mapper."""

import pytest
from env_guardian.mapper import map_env, MapReport


@pytest.fixture()
def base_env():
    return {
        "OLD_DB_HOST": "localhost",
        "OLD_DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
    }


def test_map_returns_report(base_env):
    report = map_env(base_env, {"OLD_DB_HOST": "DB_HOST"})
    assert isinstance(report, MapReport)


def test_single_key_mapped(base_env):
    report = map_env(base_env, {"OLD_DB_HOST": "DB_HOST"})
    assert "DB_HOST" in report.mapped_env()


def test_mapped_value_preserved(base_env):
    report = map_env(base_env, {"OLD_DB_HOST": "DB_HOST"})
    assert report.mapped_env()["DB_HOST"] == "localhost"


def test_multiple_keys_mapped(base_env):
    mapping = {"OLD_DB_HOST": "DB_HOST", "OLD_DB_PORT": "DB_PORT"}
    report = map_env(base_env, mapping)
    env = report.mapped_env()
    assert "DB_HOST" in env
    assert "DB_PORT" in env


def test_source_key_not_in_mapped_env(base_env):
    report = map_env(base_env, {"OLD_DB_HOST": "DB_HOST"})
    assert "OLD_DB_HOST" not in report.mapped_env()


def test_missing_source_key_is_skipped(base_env):
    report = map_env(base_env, {"NONEXISTENT": "NEW_KEY"})
    entry = next(e for e in report.entries if e.source_key == "NONEXISTENT")
    assert entry.skipped is True


def test_missing_source_key_skip_reason(base_env):
    report = map_env(base_env, {"NONEXISTENT": "NEW_KEY"})
    entry = next(e for e in report.entries if e.source_key == "NONEXISTENT")
    assert "not found" in entry.skip_reason


def test_mapped_count_correct(base_env):
    mapping = {"OLD_DB_HOST": "DB_HOST", "OLD_DB_PORT": "DB_PORT"}
    report = map_env(base_env, mapping)
    assert report.mapped_count() == 2


def test_skipped_count_correct(base_env):
    mapping = {"OLD_DB_HOST": "DB_HOST", "MISSING": "NEW_KEY"}
    report = map_env(base_env, mapping)
    assert report.skipped_count() == 1


def test_unmapped_keys_excluded_by_default(base_env):
    report = map_env(base_env, {"OLD_DB_HOST": "DB_HOST"})
    env = report.mapped_env()
    assert "APP_SECRET" not in env
    assert "OLD_DB_PORT" not in env


def test_include_unmapped_carries_through_extra_keys(base_env):
    report = map_env(base_env, {"OLD_DB_HOST": "DB_HOST"}, skip_missing=False)
    env = report.mapped_env()
    assert "APP_SECRET" in env
    assert "OLD_DB_PORT" in env


def test_summary_string(base_env):
    report = map_env(base_env, {"OLD_DB_HOST": "DB_HOST"})
    assert "mapped" in report.summary()
    assert "skipped" in report.summary()


def test_str_representation_of_entry(base_env):
    report = map_env(base_env, {"OLD_DB_HOST": "DB_HOST"})
    entry = next(e for e in report.entries if e.source_key == "OLD_DB_HOST")
    assert "OLD_DB_HOST" in str(entry)
    assert "DB_HOST" in str(entry)


def test_str_representation_of_skipped_entry(base_env):
    report = map_env(base_env, {"MISSING": "NEW_KEY"})
    entry = report.entries[0]
    assert "SKIP" in str(entry)
