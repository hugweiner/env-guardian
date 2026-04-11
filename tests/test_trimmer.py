"""Tests for env_guardian.trimmer."""

import pytest
from env_guardian.trimmer import trim_env, TrimReport


def test_clean_env_produces_no_warnings():
    env = {"KEY": "value", "OTHER": "123"}
    report = trim_env(env)
    assert report.is_clean()
    assert report.trimmed_count() == 0


def test_value_with_leading_whitespace_trimmed():
    env = {"KEY": "  hello"}
    report = trim_env(env)
    assert report.env["KEY"] == "hello"
    assert not report.is_clean()


def test_value_with_trailing_whitespace_trimmed():
    env = {"KEY": "world   "}
    report = trim_env(env)
    assert report.env["KEY"] == "world"
    assert report.trimmed_count() == 1


def test_value_with_both_sides_trimmed():
    env = {"KEY": "  both  "}
    report = trim_env(env)
    assert report.env["KEY"] == "both"


def test_warning_contains_original_and_trimmed():
    env = {"KEY": " val "}
    report = trim_env(env)
    w = report.warnings[0]
    assert w.original == " val "
    assert w.trimmed == "val"
    assert w.key == "KEY"


def test_key_with_whitespace_is_stripped():
    env = {" KEY ": "value"}
    report = trim_env(env, strip_keys=True)
    assert "KEY" in report.env
    assert " KEY " not in report.env


def test_strip_keys_disabled_preserves_original_key():
    env = {" KEY ": "value"}
    report = trim_env(env, strip_keys=False)
    assert " KEY " in report.env


def test_strip_values_disabled_preserves_original_value():
    env = {"KEY": "  value  "}
    report = trim_env(env, strip_values=False)
    assert report.env["KEY"] == "  value  "
    assert report.is_clean()


def test_collapse_whitespace_normalises_internal_spaces():
    env = {"KEY": "hello   world"}
    report = trim_env(env, collapse_whitespace=True)
    assert report.env["KEY"] == "hello world"
    assert report.trimmed_count() == 1


def test_collapse_whitespace_off_by_default():
    env = {"KEY": "hello   world"}
    report = trim_env(env)
    assert report.env["KEY"] == "hello   world"
    assert report.is_clean()


def test_multiple_keys_each_trimmed_independently():
    env = {"A": " a ", "B": "b", "C": " c"}
    report = trim_env(env)
    assert report.env["A"] == "a"
    assert report.env["B"] == "b"
    assert report.env["C"] == "c"
    assert report.trimmed_count() == 2


def test_by_key_returns_matching_warnings():
    env = {"KEY": " val ", "OTHER": "clean"}
    report = trim_env(env)
    assert len(report.by_key("KEY")) == 1
    assert len(report.by_key("OTHER")) == 0


def test_summary_clean():
    report = trim_env({"KEY": "clean"})
    assert "No trimming" in report.summary()


def test_summary_with_changes():
    report = trim_env({"KEY": " dirty "})
    assert "1" in report.summary()
