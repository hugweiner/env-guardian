"""Tests for env_guardian.validator module."""

import pytest
from env_guardian.validator import validate_env, ValidationResult, ValidationError


SAMPLE_ENV = {
    "APP_ENV": "production",
    "PORT": "8080",
    "SECRET_KEY": "s3cr3t!",
    "DEBUG": "",
}


def test_valid_env_passes():
    result = validate_env(SAMPLE_ENV, required_keys=["APP_ENV", "PORT"])
    assert result.is_valid


def test_missing_required_key():
    result = validate_env(SAMPLE_ENV, required_keys=["APP_ENV", "DATABASE_URL"])
    assert not result.is_valid
    assert any(e.key == "DATABASE_URL" for e in result.errors)


def test_multiple_missing_required_keys():
    result = validate_env(SAMPLE_ENV, required_keys=["MISSING_A", "MISSING_B"])
    assert len(result.errors) == 2


def test_non_empty_key_with_empty_value():
    result = validate_env(SAMPLE_ENV, non_empty_keys=["DEBUG"])
    assert not result.is_valid
    assert any(e.key == "DEBUG" for e in result.errors)


def test_non_empty_key_with_valid_value():
    result = validate_env(SAMPLE_ENV, non_empty_keys=["APP_ENV"])
    assert result.is_valid


def test_pattern_rule_passes():
    result = validate_env(SAMPLE_ENV, pattern_rules={"PORT": r"\d+"})
    assert result.is_valid


def test_pattern_rule_fails():
    result = validate_env(SAMPLE_ENV, pattern_rules={"APP_ENV": r"staging|development"})
    assert not result.is_valid
    assert any(e.key == "APP_ENV" for e in result.errors)


def test_pattern_rule_skips_missing_key():
    result = validate_env(SAMPLE_ENV, pattern_rules={"NONEXISTENT": r".*"})
    assert result.is_valid


def test_combined_rules_accumulate_errors():
    result = validate_env(
        SAMPLE_ENV,
        required_keys=["MISSING_KEY"],
        non_empty_keys=["DEBUG"],
        pattern_rules={"APP_ENV": r"staging"},
    )
    assert len(result.errors) == 3


def test_summary_valid():
    result = ValidationResult()
    assert result.summary() == "All validations passed."


def test_summary_with_errors():
    result = validate_env(SAMPLE_ENV, required_keys=["MISSING"])
    summary = result.summary()
    assert "1 validation error(s)" in summary
    assert "MISSING" in summary


def test_validation_error_str():
    err = ValidationError(key="FOO", message="is missing")
    assert str(err) == "[FOO] is missing"
