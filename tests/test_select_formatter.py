"""Tests for env_guardian.select_formatter."""
import json
import pytest
from env_guardian.selector import select_env
from env_guardian.select_formatter import format_text, format_json, format_csv


@pytest.fixture
def env():
    return {"DB_HOST": "localhost", "APP_SECRET": "s3cr3t", "LOG_LEVEL": "info"}


@pytest.fixture
def report(env):
    return select_env(env, prefix="DB_")


@pytest.fixture
def empty_report(env):
    return select_env(env, prefix="NOPE_")


def test_format_text_contains_header(report):
    out = format_text(report)
    assert "env-guardian select" in out


def test_format_text_contains_selected_key(report):
    out = format_text(report)
    assert "DB_HOST" in out


def test_format_text_empty_shows_no_keys(empty_report):
    out = format_text(empty_report)
    assert "No keys selected" in out


def test_format_text_contains_summary(report):
    out = format_text(report)
    assert "selected" in out


def test_format_json_valid_json(report):
    out = format_json(report)
    data = json.loads(out)
    assert "entries" in data


def test_format_json_entries_contain_key(report):
    data = json.loads(format_json(report))
    keys = [e["key"] for e in data["entries"]]
    assert "DB_HOST" in keys


def test_format_json_selected_count(report):
    data = json.loads(format_json(report))
    assert data["selected_count"] == 1


def test_format_csv_has_header(report):
    out = format_csv(report)
    assert out.startswith("key,value,reason")


def test_format_csv_contains_key(report):
    out = format_csv(report)
    assert "DB_HOST" in out
