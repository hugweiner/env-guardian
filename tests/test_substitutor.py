"""Tests for env_guardian.substitutor."""

import json
import pytest

from env_guardian.substitutor import substitute_env, SubstituteReport
from env_guardian.substitute_formatter import format_text, format_json, format_csv


# ---------------------------------------------------------------------------
# substitute_env
# ---------------------------------------------------------------------------

def test_no_placeholders_returns_same_values():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    report = substitute_env(env, {})
    assert report.env == env
    assert report.is_clean()


def test_placeholder_replaced_with_replacement():
    env = {"DB_URL": "postgres://{{DB_HOST}}:{{DB_PORT}}/mydb"}
    report = substitute_env(env, {"DB_HOST": "localhost", "DB_PORT": "5432"})
    assert report.env["DB_URL"] == "postgres://localhost:5432/mydb"
    assert report.is_clean()


def test_unresolved_placeholder_produces_warning():
    env = {"API_URL": "https://{{HOST}}/api"}
    report = substitute_env(env, {})
    assert not report.is_clean()
    assert len(report.warnings) == 1
    assert report.warnings[0].key == "API_URL"
    assert report.warnings[0].placeholder == "HOST"


def test_unresolved_placeholder_kept_by_default():
    env = {"API_URL": "https://{{HOST}}/api"}
    report = substitute_env(env, {}, keep_unresolved=True)
    assert "{{HOST}}" in report.env["API_URL"]


def test_unresolved_placeholder_removed_when_keep_false():
    env = {"API_URL": "https://{{HOST}}/api"}
    report = substitute_env(env, {}, keep_unresolved=False)
    assert "{{HOST}}" not in report.env["API_URL"]
    assert report.env["API_URL"] == "https:///api"


def test_multiple_keys_some_resolved_some_not():
    env = {
        "A": "hello {{NAME}}",
        "B": "{{GREETING}} world",
    }
    report = substitute_env(env, {"NAME": "Alice"})
    assert report.env["A"] == "hello Alice"
    assert "{{GREETING}}" in report.env["B"]
    assert len(report.warnings) == 1
    assert report.warnings[0].placeholder == "GREETING"


def test_summary_clean():
    report = substitute_env({"X": "value"}, {})
    assert "No unresolved" in report.summary()


def test_summary_with_warnings():
    report = substitute_env({"X": "{{TOKEN}}"}, {})
    assert "1 unresolved" in report.summary()


# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------

def test_format_text_contains_header():
    report = substitute_env({"K": "v"}, {})
    out = format_text(report)
    assert "Substitute Report" in out


def test_format_text_shows_env_keys():
    report = substitute_env({"MY_KEY": "hello"}, {})
    out = format_text(report)
    assert "MY_KEY=hello" in out


def test_format_text_shows_unresolved_warning():
    report = substitute_env({"X": "{{MISSING}}"}, {})
    out = format_text(report)
    assert "MISSING" in out


# ---------------------------------------------------------------------------
# format_json
# ---------------------------------------------------------------------------

def test_format_json_valid_json():
    report = substitute_env({"A": "{{B}}"}, {})
    out = format_json(report)
    data = json.loads(out)
    assert "warnings" in data
    assert data["unresolved_count"] == 1


# ---------------------------------------------------------------------------
# format_csv
# ---------------------------------------------------------------------------

def test_format_csv_has_header_row():
    report = substitute_env({}, {})
    out = format_csv(report)
    assert "key,placeholder,reason" in out


def test_format_csv_contains_warning_row():
    report = substitute_env({"URL": "http://{{HOST}}"}, {})
    out = format_csv(report)
    assert "URL" in out
    assert "HOST" in out
