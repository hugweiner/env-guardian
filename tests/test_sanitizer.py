"""Tests for env_guardian.sanitizer."""

from __future__ import annotations

import pytest

from env_guardian.sanitizer import sanitize_env, SanitizeReport


@pytest.fixture()
def clean_env() -> dict:
    return {"HOST": "localhost", "PORT": "5432", "NAME": "myapp"}


def test_clean_env_produces_no_warnings(clean_env):
    report = sanitize_env(clean_env)
    assert report.is_clean()


def test_clean_env_values_preserved(clean_env):
    report = sanitize_env(clean_env)
    assert report.env == clean_env


def test_null_byte_removed():
    env = {"SECRET": "abc\x00def"}
    report = sanitize_env(env)
    assert report.env["SECRET"] == "abcdef"


def test_null_byte_produces_warning():
    env = {"SECRET": "abc\x00def"}
    report = sanitize_env(env)
    assert not report.is_clean()
    assert report.warnings[0].key == "SECRET"
    assert "null bytes removed" in report.warnings[0].reason


def test_control_character_removed():
    env = {"LABEL": "hello\x01world"}
    report = sanitize_env(env)
    assert report.env["LABEL"] == "helloworld"


def test_control_character_produces_warning():
    env = {"LABEL": "hello\x1fworld"}
    report = sanitize_env(env)
    assert not report.is_clean()
    assert "control characters removed" in report.warnings[0].reason


def test_multiple_dirty_values_each_produce_warning():
    env = {"A": "\x00bad", "B": "ok", "C": "\x07beep"}
    report = sanitize_env(env)
    assert len(report.warnings) == 2


def test_no_strip_null_preserves_null_byte():
    env = {"KEY": "val\x00ue"}
    report = sanitize_env(env, strip_null=False)
    assert report.env["KEY"] == "val\x00ue"
    assert report.is_clean()


def test_no_strip_control_preserves_control_char():
    env = {"KEY": "val\x07ue"}
    report = sanitize_env(env, strip_control=False)
    assert report.env["KEY"] == "val\x07ue"
    assert report.is_clean()


def test_summary_clean(clean_env):
    report = sanitize_env(clean_env)
    assert report.summary() == "All values are clean."


def test_summary_dirty():
    env = {"A": "\x00", "B": "\x01"}
    report = sanitize_env(env)
    assert "2 value(s) sanitized" in report.summary()


def test_warning_str_representation():
    env = {"KEY": "a\x00b"}
    report = sanitize_env(env)
    text = str(report.warnings[0])
    assert "KEY" in text
    assert "->" in text
