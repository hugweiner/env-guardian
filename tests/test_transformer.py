"""Tests for env_guardian.transformer."""

import pytest
from env_guardian.transformer import transform_env, TransformReport


def test_clean_env_produces_no_warnings():
    env = {"HOST": "localhost", "PORT": "8080"}
    report = transform_env(env)
    assert report.is_clean()
    assert report.summary() == "No transformations applied."


def test_lowercase_key_is_uppercased():
    env = {"host": "localhost"}
    report = transform_env(env, uppercase_keys=True)
    assert "HOST" in report.env
    assert report.env["HOST"] == "localhost"


def test_lowercase_key_produces_warning():
    env = {"host": "localhost"}
    report = transform_env(env, uppercase_keys=True)
    assert not report.is_clean()
    assert any(w.key == "HOST" and "uppercased" in w.reason for w in report.warnings)


def test_uppercase_keys_disabled_preserves_original_key():
    env = {"host": "localhost"}
    report = transform_env(env, uppercase_keys=False)
    assert "host" in report.env
    assert "HOST" not in report.env


def test_value_with_leading_whitespace_is_stripped():
    env = {"HOST": "  localhost"}
    report = transform_env(env, strip_values=True)
    assert report.env["HOST"] == "localhost"


def test_value_with_trailing_whitespace_is_stripped():
    env = {"HOST": "localhost  "}
    report = transform_env(env, strip_values=True)
    assert report.env["HOST"] == "localhost"


def test_strip_values_disabled_preserves_whitespace():
    env = {"HOST": "  localhost  "}
    report = transform_env(env, strip_values=False)
    assert report.env["HOST"] == "  localhost  "


def test_trailing_slash_removed_when_enabled():
    env = {"BASE_URL": "https://example.com/"}
    report = transform_env(env, remove_trailing_slashes=True)
    assert report.env["BASE_URL"] == "https://example.com"
    assert any("trailing slash" in w.reason for w in report.warnings)


def test_trailing_slash_not_removed_by_default():
    env = {"BASE_URL": "https://example.com/"}
    report = transform_env(env)
    assert report.env["BASE_URL"] == "https://example.com/"


def test_single_slash_value_not_modified():
    env = {"PATH": "/"}
    report = transform_env(env, remove_trailing_slashes=True)
    assert report.env["PATH"] == "/"


def test_summary_shows_count():
    env = {"host": "  val  ", "port": "8080"}
    report = transform_env(env)
    assert "transformation" in report.summary()


def test_transform_warning_str():
    env = {"host": "localhost"}
    report = transform_env(env, uppercase_keys=True)
    warning_str = str(report.warnings[0])
    assert "HOST" in warning_str
    assert "uppercased" in warning_str


def test_multiple_transforms_accumulate_warnings():
    env = {"host": "  localhost/"}
    report = transform_env(env, uppercase_keys=True, strip_values=True, remove_trailing_slashes=True)
    assert len(report.warnings) >= 2
    assert report.env["HOST"] == "localhost"
