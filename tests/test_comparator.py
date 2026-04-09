"""Unit tests for env_guardian.comparator."""

import pytest

from env_guardian.comparator import compare_envs, EnvDiff


SOURCE = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc", "APP_ENV": "dev"}
TARGET_CLEAN = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc", "APP_ENV": "dev"}
TARGET_MISSING = {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "dev"}
TARGET_EXTRA = {**TARGET_CLEAN, "EXTRA_KEY": "oops"}
TARGET_MISMATCH = {**TARGET_CLEAN, "APP_ENV": "production"}


def test_clean_diff_is_clean():
    diff = compare_envs(SOURCE, TARGET_CLEAN)
    assert diff.is_clean


def test_missing_key_detected():
    diff = compare_envs(SOURCE, TARGET_MISSING)
    assert "SECRET" in diff.missing_in_target
    assert not diff.is_clean


def test_extra_key_detected():
    diff = compare_envs(SOURCE, TARGET_EXTRA)
    assert "EXTRA_KEY" in diff.extra_in_target
    assert not diff.is_clean


def test_value_mismatch_detected():
    diff = compare_envs(SOURCE, TARGET_MISMATCH)
    assert "APP_ENV" in diff.value_mismatches
    assert diff.value_mismatches["APP_ENV"] == ("dev", "production")


def test_ignore_values_skips_mismatch():
    diff = compare_envs(SOURCE, TARGET_MISMATCH, ignore_values=True)
    assert diff.is_clean


def test_ignore_keys_skips_key():
    diff = compare_envs(SOURCE, TARGET_MISSING, ignore_keys={"SECRET"})
    assert "SECRET" not in diff.missing_in_target
    assert diff.is_clean


def test_summary_clean():
    diff = EnvDiff()
    assert "No differences" in diff.summary()


def test_summary_shows_missing():
    diff = compare_envs(SOURCE, TARGET_MISSING)
    summary = diff.summary()
    assert "Missing in target" in summary
    assert "SECRET" in summary


def test_summary_shows_mismatch():
    diff = compare_envs(SOURCE, TARGET_MISMATCH)
    summary = diff.summary()
    assert "Value mismatches" in summary
    assert "APP_ENV" in summary
