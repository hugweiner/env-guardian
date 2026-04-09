"""Tests for env_guardian.interpolator."""
import pytest
from env_guardian.interpolator import interpolate, InterpolationWarning


def test_no_references_returns_same_values():
    env = {"FOO": "bar", "BAZ": "qux"}
    result = interpolate(env)
    assert result.env == env
    assert result.is_clean


def test_simple_dollar_brace_reference():
    env = {"BASE": "/app", "LOG_DIR": "${BASE}/logs"}
    result = interpolate(env)
    assert result.env["LOG_DIR"] == "/app/logs"
    assert result.is_clean


def test_simple_dollar_reference_without_braces():
    env = {"HOST": "localhost", "URL": "http://$HOST:8080"}
    result = interpolate(env)
    assert result.env["URL"] == "http://localhost:8080"
    assert result.is_clean


def test_undefined_reference_produces_warning():
    env = {"URL": "http://${MISSING_HOST}:8080"}
    result = interpolate(env)
    assert not result.is_clean
    assert len(result.warnings) == 1
    w = result.warnings[0]
    assert w.key == "URL"
    assert w.ref == "MISSING_HOST"
    assert "undefined" in w.message


def test_undefined_reference_keeps_original_placeholder():
    env = {"URL": "http://${GHOST}"}
    result = interpolate(env)
    assert result.env["URL"] == "http://${GHOST}"


def test_chained_references():
    env = {"A": "hello", "B": "${A} world", "C": "${B}!"}
    result = interpolate(env)
    assert result.env["C"] == "hello world!"
    assert result.is_clean


def test_multiple_refs_in_single_value():
    env = {"PROTO": "https", "HOST": "example.com", "URL": "${PROTO}://${HOST}"}
    result = interpolate(env)
    assert result.env["URL"] == "https://example.com"
    assert result.is_clean


def test_self_referencing_key_does_not_crash():
    # LOOP references itself — depth guard should trigger
    env = {"LOOP": "${LOOP}/child"}
    result = interpolate(env)
    # Should not raise; may produce a warning
    assert isinstance(result.is_clean, bool)


def test_summary_clean():
    result = interpolate({"KEY": "value"})
    assert "no unresolved" in result.summary().lower()


def test_summary_with_warnings():
    result = interpolate({"KEY": "${NOPE}"})
    assert "1 warning" in result.summary()


def test_warning_str():
    w = InterpolationWarning(key="FOO", ref="BAR", message="undefined reference")
    assert "FOO" in str(w)
    assert "BAR" in str(w)
