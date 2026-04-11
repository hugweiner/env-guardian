"""Tests for env_guardian.whitelister."""
import json

import pytest

from env_guardian.whitelister import whitelist_env
from env_guardian.whitelist_formatter import format_csv, format_json, format_text


@pytest.fixture()
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "s3cr3t",
        "DEBUG": "true",
        "ALLOWED_HOSTS": "*",
    }


def test_whitelist_returns_report(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST", "DB_PORT"])
    assert report is not None
    assert len(report.entries) == len(mixed_env)


def test_allowed_keys_are_included(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST", "DB_PORT"])
    assert report.allowed_env == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_blocked_keys_not_in_allowed_env(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST"])
    assert "SECRET_KEY" not in report.allowed_env
    assert "DEBUG" not in report.allowed_env


def test_allowed_count_correct(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST", "DB_PORT", "DEBUG"])
    assert report.allowed_count == 3


def test_blocked_count_correct(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST", "DB_PORT", "DEBUG"])
    assert report.blocked_count == 2


def test_is_clean_when_all_allowed(mixed_env):
    all_keys = list(mixed_env.keys())
    report = whitelist_env(mixed_env, all_keys)
    assert report.is_clean()


def test_not_clean_when_some_blocked(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST"])
    assert not report.is_clean()


def test_blocked_entry_has_reason(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST"])
    blocked = [e for e in report.entries if not e.allowed]
    assert all(e.reason for e in blocked)


def test_case_insensitive_matching():
    env = {"db_host": "localhost", "SECRET": "abc"}
    report = whitelist_env(env, ["DB_HOST"], case_sensitive=False)
    assert report.allowed_count == 1
    assert "db_host" in report.allowed_env


def test_empty_env_produces_no_entries():
    report = whitelist_env({}, ["DB_HOST"])
    assert len(report.entries) == 0
    assert report.is_clean()


def test_empty_whitelist_blocks_all(mixed_env):
    report = whitelist_env(mixed_env, [])
    assert report.allowed_count == 0
    assert report.blocked_count == len(mixed_env)


def test_summary_string(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST", "DB_PORT"])
    s = report.summary()
    assert "2" in s
    assert "allowed" in s


# --- formatter tests ---


def test_format_text_contains_header(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST"])
    text = format_text(report)
    assert "Whitelist Report" in text


def test_format_text_marks_allowed_key(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST"])
    text = format_text(report)
    assert "✓" in text


def test_format_text_marks_blocked_key(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST"])
    text = format_text(report)
    assert "✗" in text


def test_format_json_valid_json(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST", "DB_PORT"])
    data = json.loads(format_json(report))
    assert "entries" in data
    assert data["summary"]["allowed"] == 2


def test_format_csv_has_header(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST"])
    csv_text = format_csv(report)
    assert csv_text.startswith("key,value,allowed,reason")


def test_format_csv_row_count(mixed_env):
    report = whitelist_env(mixed_env, ["DB_HOST"])
    lines = [l for l in format_csv(report).splitlines() if l]
    assert len(lines) == len(mixed_env) + 1  # header + data rows
