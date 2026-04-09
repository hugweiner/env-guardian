"""Tests for env_guardian.merger."""

import pytest
from env_guardian.merger import merge_envs, MergeResult, MergeConflict


ENV_A = {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"}
ENV_B = {"HOST": "prod.example.com", "PORT": "443", "SECRET": "abc123"}
ENV_C = {"REGION": "us-east-1", "DEBUG": "false"}


def test_merge_single_source_returns_same_env():
    result = merge_envs([("base", ENV_A)])
    assert result.merged == ENV_A
    assert not result.has_conflicts()


def test_merge_last_wins_strategy():
    result = merge_envs([("a", ENV_A), ("b", ENV_B)], strategy="last_wins")
    assert result.merged["HOST"] == "prod.example.com"
    assert result.merged["PORT"] == "443"
    assert result.merged["DEBUG"] == "true"
    assert result.merged["SECRET"] == "abc123"


def test_merge_first_wins_strategy():
    result = merge_envs([("a", ENV_A), ("b", ENV_B)], strategy="first_wins")
    assert result.merged["HOST"] == "localhost"
    assert result.merged["PORT"] == "8080"


def test_merge_detects_conflicts():
    result = merge_envs([("a", ENV_A), ("b", ENV_B)])
    conflict_keys = {c.key for c in result.conflicts}
    assert "HOST" in conflict_keys
    assert "PORT" in conflict_keys
    assert "DEBUG" not in conflict_keys  # same value not a conflict


def test_merge_no_conflict_when_values_identical():
    env1 = {"KEY": "value"}
    env2 = {"KEY": "value"}
    result = merge_envs([("x", env1), ("y", env2)])
    assert not result.has_conflicts()


def test_merge_three_sources_combined_keys():
    result = merge_envs([("a", ENV_A), ("b", ENV_B), ("c", ENV_C)])
    assert "HOST" in result.merged
    assert "SECRET" in result.merged
    assert "REGION" in result.merged


def test_merge_raise_on_conflict():
    with pytest.raises(ValueError, match="Merge conflict"):
        merge_envs([("a", ENV_A), ("b", ENV_B)], raise_on_conflict=True)


def test_merge_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        merge_envs([("a", ENV_A)], strategy="random")


def test_merge_sources_used_recorded():
    result = merge_envs([("base", ENV_A), ("override", ENV_B)])
    assert result.sources_used == ["base", "override"]


def test_merge_summary_contains_key_info():
    result = merge_envs([("a", ENV_A), ("b", ENV_B)])
    summary = result.summary()
    assert "2 source(s)" in summary
    assert "Conflicts" in summary


def test_merge_conflict_str():
    conflict = MergeConflict(key="HOST", values=[("a", "localhost"), ("b", "prod")])
    text = str(conflict)
    assert "HOST" in text
    assert "localhost" in text
    assert "prod" in text


def test_merge_empty_sources_returns_empty():
    result = merge_envs([])
    assert result.merged == {}
    assert not result.has_conflicts()
