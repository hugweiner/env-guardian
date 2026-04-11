"""Tests for env_guardian.filter_formatter."""
from __future__ import annotations

import csv
import io
import json

import pytest

from env_guardian.filter_formatter import format_csv, format_json, format_text
from env_guardian.filterer import filter_env


@pytest.fixture()
def env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "SECRET_KEY": "abc123",
    }


@pytest.fixture()
def report(env):
    return filter_env(env, prefixes=["DB_"])


@pytest.fixture()
def empty_report(env):
    return filter_env(env, prefixes=["NOPE_"])


def test_format_text_contains_header(report):
    out = format_text(report)
    assert "Filter Report" in out


def test_format_text_contains_matched_keys(report):
    out = format_text(report)
    assert "DB_HOST" in out
    assert "DB_PORT" in out


def test_format_text_excludes_non_matched(report):
    out = format_text(report)
    assert "SECRET_KEY" not in out or "Excluded" in out


def test_format_text_empty_shows_no_keys_message(empty_report):
    out = format_text(empty_report)
    assert "No keys matched" in out


def test_format_text_shows_summary(report):
    out = format_text(report)
    assert "matched" in out


def test_format_json_valid_json(report):
    out = format_json(report)
    data = json.loads(out)
    assert "matched" in data
    assert "excluded" in data
    assert "summary" in data


def test_format_json_matched_entries(report):
    data = json.loads(format_json(report))
    keys = [e["key"] for e in data["matched"]]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys


def test_format_json_excluded_keys(report):
    data = json.loads(format_json(report))
    assert "SECRET_KEY" in data["excluded"]


def test_format_csv_has_header(report):
    out = format_csv(report)
    reader = csv.reader(io.StringIO(out))
    header = next(reader)
    assert header == ["key", "value", "matched_rule"]


def test_format_csv_has_correct_rows(report):
    out = format_csv(report)
    reader = csv.reader(io.StringIO(out))
    next(reader)  # skip header
    rows = list(reader)
    keys = [r[0] for r in rows]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
