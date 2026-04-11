"""Tests for env_guardian.deprecator."""
from __future__ import annotations

import pytest

from env_guardian.deprecator import DeprecateReport, DeprecationWarning_, deprecate_env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_env(**kwargs: str) -> dict:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_clean_env_produces_no_warnings():
    env = _make_env(DATABASE_URL="postgres://localhost/db", DEBUG="true")
    report = deprecate_env(env)
    assert report.is_clean()


def test_deprecated_key_detected():
    env = _make_env(DB_HOST="localhost")
    report = deprecate_env(env)
    assert not report.is_clean()
    assert "DB_HOST" in report.deprecated_keys()


def test_multiple_deprecated_keys_detected():
    env = _make_env(DB_HOST="localhost", DB_USER="admin", DB_PASS="secret")
    report = deprecate_env(env)
    assert len(report.warnings) == 3


def test_non_deprecated_key_not_flagged():
    env = _make_env(DATABASE_URL="postgres://localhost/db")
    report = deprecate_env(env)
    assert "DATABASE_URL" not in report.deprecated_keys()


def test_replacement_is_populated():
    env = _make_env(DEBUG_MODE="true")
    report = deprecate_env(env)
    w = report.by_key()["DEBUG_MODE"]
    assert w.replacement == "DEBUG"


def test_reason_is_populated():
    env = _make_env(APP_ENV="production")
    report = deprecate_env(env)
    w = report.by_key()["APP_ENV"]
    assert "Renamed" in w.reason


def test_summary_clean():
    report = deprecate_env({})
    assert "No deprecated" in report.summary()


def test_summary_with_warnings():
    env = _make_env(SECRET="abc")
    report = deprecate_env(env)
    assert "1 deprecated" in report.summary()


# ---------------------------------------------------------------------------
# Extra rules
# ---------------------------------------------------------------------------

def test_extra_rule_detected():
    env = _make_env(OLD_API_KEY="xyz")
    extra = {"OLD_API_KEY": ("Replaced by API_KEY", "API_KEY")}
    report = deprecate_env(env, extra_rules=extra)
    assert "OLD_API_KEY" in report.deprecated_keys()


def test_extra_rule_replacement_stored():
    env = _make_env(OLD_API_KEY="xyz")
    extra = {"OLD_API_KEY": ("Replaced by API_KEY", "API_KEY")}
    report = deprecate_env(env, extra_rules=extra)
    assert report.by_key()["OLD_API_KEY"].replacement == "API_KEY"


def test_extra_rule_without_replacement():
    env = _make_env(LEGACY_FLAG="1")
    extra = {"LEGACY_FLAG": ("No longer used", None)}
    report = deprecate_env(env, extra_rules=extra)
    w = report.by_key()["LEGACY_FLAG"]
    assert w.replacement is None


# ---------------------------------------------------------------------------
# DeprecationWarning_ __str__
# ---------------------------------------------------------------------------

def test_str_with_replacement():
    w = DeprecationWarning_(key="OLD", reason="Renamed", replacement="NEW")
    assert "OLD" in str(w)
    assert "NEW" in str(w)


def test_str_without_replacement():
    w = DeprecationWarning_(key="OLD", reason="Obsolete")
    result = str(w)
    assert "OLD" in result
    assert "instead" not in result
