"""Tests for env_guardian.truncator."""

import pytest
from env_guardian.truncator import TruncateWarning, truncate_env


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _env(**kwargs: str):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# basic behaviour
# ---------------------------------------------------------------------------

def test_clean_env_produces_no_warnings():
    env = _env(SHORT="hi", MEDIUM="hello world")
    report = truncate_env(env, max_length=64)
    assert report.is_clean()
    assert report.truncated_count() == 0


def test_short_value_unchanged():
    env = _env(KEY="abc")
    report = truncate_env(env, max_length=10)
    assert report.env["KEY"] == "abc"


def test_long_value_is_truncated():
    env = _env(KEY="A" * 100)
    report = truncate_env(env, max_length=20)
    assert len(report.env["KEY"]) == 20


def test_truncated_value_ends_with_suffix():
    env = _env(KEY="B" * 80)
    report = truncate_env(env, max_length=30, suffix="...")
    assert report.env["KEY"].endswith("...")


def test_warning_recorded_for_truncated_key():
    env = _env(TOKEN="X" * 50)
    report = truncate_env(env, max_length=10)
    assert "TOKEN" in report.truncated_keys()


def test_truncated_count_correct():
    env = _env(A="a" * 100, B="b" * 5, C="c" * 200)
    report = truncate_env(env, max_length=50)
    assert report.truncated_count() == 2


def test_original_length_stored_in_warning():
    env = _env(KEY="Z" * 70)
    report = truncate_env(env, max_length=20)
    warning = report.warnings[0]
    assert warning.original_length == 70


def test_truncated_length_stored_in_warning():
    env = _env(KEY="Z" * 70)
    report = truncate_env(env, max_length=20, suffix="...")
    warning = report.warnings[0]
    assert warning.truncated_length == 20


def test_summary_clean():
    report = truncate_env({}, max_length=64)
    assert "No values truncated" in report.summary()


def test_summary_with_truncations():
    env = _env(LONG="L" * 200)
    report = truncate_env(env, max_length=10)
    assert "1 value(s) truncated" in report.summary()


def test_is_clean_false_when_truncations_exist():
    env = _env(LONG="L" * 200)
    report = truncate_env(env, max_length=10)
    assert not report.is_clean()


def test_invalid_max_length_raises():
    with pytest.raises(ValueError):
        truncate_env({"KEY": "value"}, max_length=0)


def test_warning_str_contains_key():
    w = TruncateWarning(key="MY_KEY", original_length=100, truncated_length=20)
    assert "MY_KEY" in str(w)


def test_custom_suffix_applied():
    env = _env(KEY="A" * 50)
    report = truncate_env(env, max_length=15, suffix="--")
    assert report.env["KEY"].endswith("--")
    assert len(report.env["KEY"]) == 15
