"""Tests for env_guardian.sanitize_formatter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from env_guardian.sanitizer import sanitize_env
from env_guardian.sanitize_formatter import format_text, format_json, format_csv


@pytest.fixture()
def clean_report():
    return sanitize_env({"HOST": "localhost", "PORT": "8080"})


@pytest.fixture()
def dirty_report():
    return sanitize_env({"SECRET": "abc\x00def", "LABEL": "hi\x01there", "SAFE": "ok"})


def test_format_text_clean_shows_no_issues(clean_report):
    out = format_text(clean_report)
    assert "clean" in out.lower()


def test_format_text_contains_header(dirty_report):
    out = format_text(dirty_report)
    assert "Sanitize Report" in out


def test_format_text_shows_sanitized_count(dirty_report):
    out = format_text(dirty_report)
    assert "2" in out


def test_format_text_contains_key_names(dirty_report):
    out = format_text(dirty_report)
    assert "SECRET" in out
    assert "LABEL" in out


def test_format_text_does_not_include_clean_key(dirty_report):
    out = format_text(dirty_report)
    assert "SAFE" not in out


def test_format_json_valid_json(dirty_report):
    out = format_json(dirty_report)
    data = json.loads(out)
    assert isinstance(data, dict)


def test_format_json_contains_warnings(dirty_report):
    out = format_json(dirty_report)
    data = json.loads(out)
    assert len(data["warnings"]) == 2


def test_format_json_clean_flag_true(clean_report):
    data = json.loads(format_json(clean_report))
    assert data["clean"] is True


def test_format_json_clean_flag_false(dirty_report):
    data = json.loads(format_json(dirty_report))
    assert data["clean"] is False


def test_format_csv_has_header(dirty_report):
    out = format_csv(dirty_report)
    reader = csv.reader(io.StringIO(out))
    header = next(reader)
    assert "key" in header
    assert "reason" in header


def test_format_csv_row_count(dirty_report):
    out = format_csv(dirty_report)
    reader = csv.reader(io.StringIO(out))
    rows = list(reader)
    assert len(rows) == 3  # header + 2 warnings
