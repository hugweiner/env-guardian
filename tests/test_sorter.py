"""Tests for env_guardian.sorter."""

import pytest
from env_guardian.sorter import sort_env, SortReport


@pytest.fixture
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "APP_NAME": "guardian",
        "DB_PORT": "5432",
        "ZEBRA": "1",
        "APP_ENV": "production",
        "LOG_LEVEL": "info",
    }


def test_sort_returns_report(mixed_env):
    report = sort_env(mixed_env)
    assert isinstance(report, SortReport)


def test_alpha_strategy_sorts_keys(mixed_env):
    report = sort_env(mixed_env, strategy="alpha")
    assert list(report.sorted_env.keys()) == sorted(mixed_env.keys())


def test_alpha_strategy_is_default(mixed_env):
    report = sort_env(mixed_env)
    assert report.strategy == "alpha"
    assert list(report.sorted_env.keys()) == sorted(mixed_env.keys())


def test_length_strategy_sorts_by_key_length(mixed_env):
    report = sort_env(mixed_env, strategy="length")
    keys = list(report.sorted_env.keys())
    lengths = [len(k) for k in keys]
    assert lengths == sorted(lengths)


def test_value_strategy_sorts_by_value(mixed_env):
    report = sort_env(mixed_env, strategy="value")
    values = list(report.sorted_env.values())
    assert values == sorted(values)


def test_reverse_flag_reverses_order(mixed_env):
    forward = sort_env(mixed_env, strategy="alpha", reverse=False)
    backward = sort_env(mixed_env, strategy="alpha", reverse=True)
    assert list(forward.sorted_env.keys()) == list(reversed(list(backward.sorted_env.keys())))


def test_original_order_preserved_in_report(mixed_env):
    report = sort_env(mixed_env)
    assert report.original_order == list(mixed_env.keys())


def test_sorted_env_contains_all_keys(mixed_env):
    report = sort_env(mixed_env)
    assert set(report.sorted_env.keys()) == set(mixed_env.keys())


def test_sorted_env_values_unchanged(mixed_env):
    report = sort_env(mixed_env)
    for key, value in mixed_env.items():
        assert report.sorted_env[key] == value


def test_group_by_prefix_creates_groups(mixed_env):
    report = sort_env(mixed_env, group_by_prefix=True)
    assert "DB" in report.groups
    assert "APP" in report.groups


def test_group_by_prefix_groups_keys_correctly(mixed_env):
    report = sort_env(mixed_env, group_by_prefix=True)
    assert set(report.groups["DB"]) == {"DB_HOST", "DB_PORT"}
    assert set(report.groups["APP"]) == {"APP_NAME", "APP_ENV"}


def test_group_names_returns_sorted_list(mixed_env):
    report = sort_env(mixed_env, group_by_prefix=True)
    assert report.group_names() == sorted(report.groups.keys())


def test_summary_no_groups(mixed_env):
    report = sort_env(mixed_env, strategy="alpha")
    summary = report.summary()
    assert "alpha" in summary
    assert str(len(mixed_env)) in summary


def test_summary_with_groups(mixed_env):
    report = sort_env(mixed_env, group_by_prefix=True)
    summary = report.summary()
    assert "group" in summary


def test_invalid_strategy_raises_value_error(mixed_env):
    with pytest.raises(ValueError, match="Unknown strategy"):
        sort_env(mixed_env, strategy="random")


def test_empty_env_sorts_cleanly():
    report = sort_env({})
    assert report.sorted_env == {}
    assert report.original_order == []
