"""Tests for env_guardian.trim_formatter."""

import json
import csv
import io
import pytest

from env_guardian.trimmer import trim_env
from env_guardian.trim_formatter import format_text, format_json, format_csv


@pytest.fixture
def clean_report():
    return trim_env({"KEY": "value", "OTHER": "123"})


@pytest.fixture
def dirty_report():
    return trim_env({"ALPHA": " hello ", "BETA": "world  ", "GAMMA": "clean"})


def test_format_text_clean_shows_no_warnings(clean_report):
    text = format_text(clean_report)
    assert "No trimming needed" in text


def test_format_text_contains_header(dirty_report):
    text = format_text(dirty_report)
    assert "Trim Report" in text


def test_format_text_shows_trimmed_count(dirty_report):
    text = format_text(dirty_report)
    assert "2" in text


def test_format_text_contains_key_names(dirty_report):
    text = format_text(dirty_report)
    assert "ALPHA" in text
    assert "BETA" in text


def test_format_json_valid_json(dirty_report):
    result = format_json(dirty_report)
    data = json.loads(result)
    assert "warnings" in data
    assert "env" in data
    assert "trimmed_count" in data


def test_format_json_clean_has_empty_warnings(clean_report):
    data = json.loads(format_json(clean_report))
    assert data["warnings"] == []
    assert data["trimmed_count"] == 0


def test_format_json_warnings_contain_expected_fields(dirty_report):
    data = json.loads(format_json(dirty_report))
    for w in data["warnings"]:
        assert "key" in w
        assert "original" in w
        assert "trimmed" in w
        assert "reason" in w


def test_format_csv_has_header(dirty_report):
    result = format_csv(dirty_report)
    reader = csv.reader(io.StringIO(result))
    header = next(reader)
    assert header == ["key", "original", "trimmed", "reason"]


def test_format_csv_row_count_matches_warnings(dirty_report):
    result = format_csv(dirty_report)
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    # header + 2 warnings
    assert len(rows) == 3


def test_format_csv_clean_has_only_header(clean_report):
    result = format_csv(clean_report)
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) == 1
