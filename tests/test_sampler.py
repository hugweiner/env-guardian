"""Tests for env_guardian.sampler and env_guardian.sample_formatter."""
import json

import pytest

from env_guardian.sampler import sample_env
from env_guardian.sample_formatter import format_csv, format_json, format_text


@pytest.fixture()
def mixed_env():
    return {
        "APP_NAME": "guardian",
        "APP_VERSION": "1.0",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "s3cr3t",
        "REDIS_URL": "redis://localhost",
        "LOG_LEVEL": "INFO",
    }


def test_sample_returns_report(mixed_env):
    report = sample_env(mixed_env, n=3)
    assert report is not None
    assert report.total_keys == len(mixed_env)


def test_random_strategy_respects_n(mixed_env):
    report = sample_env(mixed_env, n=3, strategy="random", seed=42)
    assert report.sampled_count() == 3


def test_random_strategy_is_default(mixed_env):
    report = sample_env(mixed_env, n=2, seed=0)
    assert report.strategy == "random"
    assert report.sampled_count() == 2


def test_first_strategy_returns_alphabetical_head(mixed_env):
    report = sample_env(mixed_env, n=2, strategy="first")
    keys = [e.key for e in report.entries]
    assert "APP_NAME" in keys
    assert "APP_VERSION" in keys


def test_last_strategy_returns_alphabetical_tail(mixed_env):
    report = sample_env(mixed_env, n=2, strategy="last")
    keys = [e.key for e in report.entries]
    assert "REDIS_URL" in keys


def test_prefix_strategy_filters_by_prefix(mixed_env):
    report = sample_env(mixed_env, n=99, strategy="prefix", prefix="DB_")
    keys = [e.key for e in report.entries]
    assert set(keys) == {"DB_HOST", "DB_PORT", "DB_PASSWORD"}


def test_prefix_strategy_no_match_returns_empty(mixed_env):
    report = sample_env(mixed_env, n=3, strategy="prefix", prefix="MISSING_")
    assert report.sampled_count() == 0


def test_sampled_env_dict_has_correct_values(mixed_env):
    report = sample_env(mixed_env, n=2, strategy="first")
    env = report.sampled_env()
    for key, value in env.items():
        assert mixed_env[key] == value


def test_entry_index_matches_sorted_position(mixed_env):
    sorted_keys = sorted(mixed_env.keys())
    report = sample_env(mixed_env, n=len(mixed_env), strategy="first")
    for entry in report.entries:
        assert entry.index == sorted_keys.index(entry.key)


def test_n_larger_than_env_does_not_raise(mixed_env):
    report = sample_env(mixed_env, n=1000, strategy="last")
    assert report.sampled_count() == len(mixed_env)


def test_summary_contains_strategy(mixed_env):
    report = sample_env(mixed_env, n=3, strategy="first")
    assert "first" in report.summary()


# --- formatter tests ---

def test_format_text_contains_header(mixed_env):
    report = sample_env(mixed_env, n=3, strategy="first")
    text = format_text(report)
    assert "Env Sample" in text


def test_format_text_contains_all_sampled_keys(mixed_env):
    report = sample_env(mixed_env, n=3, strategy="first")
    text = format_text(report)
    for entry in report.entries:
        assert entry.key in text


def test_format_text_empty_report(mixed_env):
    report = sample_env(mixed_env, n=0, strategy="first")
    text = format_text(report)
    assert "no keys sampled" in text


def test_format_json_valid_json(mixed_env):
    report = sample_env(mixed_env, n=3, strategy="first")
    data = json.loads(format_json(report))
    assert data["strategy"] == "first"
    assert data["sampled_count"] == 3
    assert len(data["entries"]) == 3


def test_format_csv_has_header_and_rows(mixed_env):
    report = sample_env(mixed_env, n=2, strategy="first")
    csv_text = format_csv(report)
    lines = [l for l in csv_text.strip().splitlines() if l]
    assert lines[0] == "key,value,index"
    assert len(lines) == 3  # header + 2 rows
