"""Tests for env_guardian.coercer."""
import pytest
from env_guardian.coercer import coerce_env, CoerceReport


def test_coerce_returns_report():
    report = coerce_env({"KEY": "value"})
    assert isinstance(report, CoerceReport)


def test_clean_env_produces_no_warnings():
    report = coerce_env({"KEY": "value", "OTHER": "123"})
    assert report.is_clean()
    assert report.coerced_count() == 0


def test_bool_true_variants_normalised():
    for variant in ("True", "TRUE", "Yes", "YES", "1", "On", "ON"):
        report = coerce_env({"FLAG": variant})
        assert report.env["FLAG"] == "true", f"Expected 'true' for {variant!r}"


def test_bool_false_variants_normalised():
    for variant in ("False", "FALSE", "No", "NO", "0", "Off", "OFF"):
        report = coerce_env({"FLAG": variant})
        assert report.env["FLAG"] == "false", f"Expected 'false' for {variant!r}"


def test_already_canonical_bool_produces_no_warning():
    report = coerce_env({"FLAG": "true"})
    assert report.is_clean()


def test_leading_whitespace_stripped():
    report = coerce_env({"KEY": "  hello"})
    assert report.env["KEY"] == "hello"
    assert report.coerced_count() == 1


def test_trailing_whitespace_stripped():
    report = coerce_env({"KEY": "hello   "})
    assert report.env["KEY"] == "hello"
    assert report.coerced_count() == 1


def test_both_sides_whitespace_stripped():
    report = coerce_env({"KEY": "  hello  "})
    assert report.env["KEY"] == "hello"
    assert report.coerced_count() == 1


def test_internal_spaces_collapsed():
    report = coerce_env({"KEY": "hello   world"})
    assert report.env["KEY"] == "hello world"
    assert report.coerced_count() == 1


def test_warning_contains_original_and_coerced():
    report = coerce_env({"KEY": "  value  "})
    assert len(report.warnings) == 1
    w = report.warnings[0]
    assert w.original == "  value  "
    assert w.coerced == "value"
    assert w.key == "KEY"


def test_summary_clean():
    report = coerce_env({"KEY": "clean"})
    assert "No coercions" in report.summary()


def test_summary_with_coercions():
    report = coerce_env({"A": "  x", "B": "TRUE"})
    assert "coercion" in report.summary()


def test_multiple_keys_coerced_independently():
    env = {"A": "  yes  ", "B": "normal", "C": "  hello"}
    report = coerce_env(env)
    assert report.env["A"] == "true"
    assert report.env["B"] == "normal"
    assert report.env["C"] == "hello"
    assert report.coerced_count() == 2


def test_original_env_not_mutated():
    env = {"KEY": "  hello  "}
    coerce_env(env)
    assert env["KEY"] == "  hello  "
