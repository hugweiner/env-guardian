"""Tests for env_guardian.freezer and env_guardian.freeze_formatter."""
import json

import pytest

from env_guardian.freezer import (
    FreezeReport,
    FreezeViolation,
    _compute_checksum,
    check_frozen,
    freeze_env,
)
from env_guardian.freeze_formatter import format_csv, format_json, format_text


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def base_env():
    return {"DATABASE_URL": "postgres://localhost/db", "SECRET_KEY": "s3cr3t", "DEBUG": "false"}


@pytest.fixture()
def frozen(base_env):
    return freeze_env(base_env)


# ---------------------------------------------------------------------------
# freezer tests
# ---------------------------------------------------------------------------

def test_freeze_captures_all_keys(base_env, frozen):
    assert set(frozen.frozen_env.keys()) == set(base_env.keys())


def test_freeze_stores_correct_values(base_env, frozen):
    for key, val in base_env.items():
        assert frozen.frozen_env[key] == val


def test_freeze_computes_checksum(frozen):
    assert len(frozen.checksum) == 64  # SHA-256 hex digest


def test_checksum_is_deterministic(base_env):
    assert _compute_checksum(base_env) == _compute_checksum(base_env)


def test_checksum_changes_when_value_changes(base_env):
    modified = {**base_env, "DEBUG": "true"}
    assert _compute_checksum(base_env) != _compute_checksum(modified)


def test_clean_check_produces_no_violations(base_env, frozen):
    result = check_frozen(frozen, base_env)
    assert result.is_clean()
    assert result.violation_count() == 0


def test_changed_value_detected(base_env, frozen):
    mutated = {**base_env, "SECRET_KEY": "different"}
    result = check_frozen(frozen, mutated)
    assert not result.is_clean()
    keys = [v.key for v in result.violations]
    assert "SECRET_KEY" in keys


def test_removed_key_detected(base_env, frozen):
    shrunk = {k: v for k, v in base_env.items() if k != "DEBUG"}
    result = check_frozen(frozen, shrunk)
    assert any(v.key == "DEBUG" and "removed" in v.reason for v in result.violations)


def test_extra_key_flagged_by_default(base_env, frozen):
    expanded = {**base_env, "NEW_KEY": "new_value"}
    result = check_frozen(frozen, expanded)
    assert any(v.key == "NEW_KEY" for v in result.violations)


def test_extra_key_allowed_when_flag_set(base_env, frozen):
    expanded = {**base_env, "NEW_KEY": "new_value"}
    result = check_frozen(frozen, expanded, allow_extra=True)
    assert result.is_clean()


def test_summary_clean(base_env, frozen):
    result = check_frozen(frozen, base_env)
    assert "intact" in result.summary()


def test_summary_with_violations(base_env, frozen):
    result = check_frozen(frozen, {})
    assert "violation" in result.summary()


# ---------------------------------------------------------------------------
# freeze_formatter tests
# ---------------------------------------------------------------------------

def test_format_text_contains_header(base_env, frozen):
    result = check_frozen(frozen, base_env)
    text = format_text(result)
    assert "Freeze Check Report" in text


def test_format_text_clean_shows_no_violations(base_env, frozen):
    result = check_frozen(frozen, base_env)
    text = format_text(result)
    assert "No violations" in text


def test_format_text_shows_violations(base_env, frozen):
    mutated = {**base_env, "SECRET_KEY": "oops"}
    result = check_frozen(frozen, mutated)
    text = format_text(result)
    assert "SECRET_KEY" in text
    assert "VIOLATIONS FOUND" in text


def test_format_json_valid_json(base_env, frozen):
    result = check_frozen(frozen, base_env)
    data = json.loads(format_json(result))
    assert data["is_clean"] is True
    assert data["violation_count"] == 0
    assert "checksum" in data


def test_format_json_includes_violations(base_env, frozen):
    mutated = {**base_env, "DEBUG": "true"}
    result = check_frozen(frozen, mutated)
    data = json.loads(format_json(result))
    assert data["is_clean"] is False
    assert any(v["key"] == "DEBUG" for v in data["violations"])


def test_format_csv_contains_header(base_env, frozen):
    result = check_frozen(frozen, base_env)
    csv_text = format_csv(result)
    assert csv_text.startswith("key,expected,actual,reason")


def test_format_csv_violations_listed(base_env, frozen):
    mutated = {k: v for k, v in base_env.items() if k != "SECRET_KEY"}
    result = check_frozen(frozen, mutated)
    csv_text = format_csv(result)
    assert "SECRET_KEY" in csv_text
