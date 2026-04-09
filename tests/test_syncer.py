"""Tests for env_guardian.syncer module."""

import pytest
from env_guardian.syncer import sync_envs, SyncResult


SOURCE = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
TARGET = {"HOST": "prod.example.com", "SECRET": "abc123"}


def test_sync_adds_missing_keys():
    merged, result = sync_envs(SOURCE, TARGET)
    assert "PORT" in merged
    assert "DEBUG" in merged
    assert "PORT" in result.added
    assert "DEBUG" in result.added


def test_sync_overwrites_existing_by_default():
    merged, result = sync_envs(SOURCE, TARGET)
    assert merged["HOST"] == "localhost"
    assert "HOST" in result.updated


def test_sync_no_overwrite_skips_existing():
    merged, result = sync_envs(SOURCE, TARGET, overwrite=False)
    assert merged["HOST"] == "prod.example.com"
    assert "HOST" in result.skipped


def test_sync_preserves_target_only_keys():
    merged, result = sync_envs(SOURCE, TARGET)
    assert "SECRET" in merged
    assert "SECRET" not in result.removed


def test_sync_remove_extra_drops_target_only_keys():
    merged, result = sync_envs(SOURCE, TARGET, remove_extra=True)
    assert "SECRET" not in merged
    assert "SECRET" in result.removed


def test_sync_ignore_keys_skips_them():
    merged, result = sync_envs(SOURCE, TARGET, ignore_keys=["PORT"])
    assert "PORT" not in merged
    assert "PORT" in result.skipped


def test_sync_result_has_changes_true():
    _, result = sync_envs(SOURCE, TARGET)
    assert result.has_changes is True


def test_sync_result_has_changes_false():
    same = {"HOST": "prod.example.com", "SECRET": "abc123"}
    _, result = sync_envs(same, TARGET)
    assert result.has_changes is False


def test_sync_result_summary_no_changes():
    same = {"HOST": "prod.example.com", "SECRET": "abc123"}
    _, result = sync_envs(same, TARGET)
    assert result.summary() == "No changes."


def test_sync_result_summary_contains_sections():
    _, result = sync_envs(SOURCE, TARGET)
    summary = result.summary()
    assert "Added" in summary or "Updated" in summary


def test_sync_empty_source_no_changes():
    merged, result = sync_envs({}, TARGET)
    assert merged == TARGET
    assert not result.has_changes
