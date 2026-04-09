"""Tests for env_guardian.profile_formatter."""

import csv
import io
import json

import pytest
from env_guardian.profiler import profile_env
from env_guardian.profile_formatter import format_text, format_json, format_csv


SAMPLE_ENV = {
    "SECRET_KEY": "s3cr3t",
    "DATABASE_URL": "postgres://localhost/db",
    "DEBUG": "true",
    "PORT": "8080",
    "EMPTY_VAR": "",
}


@pytest.fixture
def report():
    return profile_env(SAMPLE_ENV)


def test_format_text_contains_header(report):
    output = format_text(report)
    assert "Environment Profile" in output


def test_format_text_contains_all_keys(report):
    output = format_text(report)
    for key in SAMPLE_ENV:
        assert key in output


def test_format_text_shows_summary_counts(report):
    output = format_text(report)
    assert str(report.total) in output


def test_format_json_valid_json(report):
    output = format_json(report)
    data = json.loads(output)
    assert "total" in data
    assert "entries" in data
    assert "categories" in data


def test_format_json_total_matches(report):
    data = json.loads(format_json(report))
    assert data["total"] == report.total


def test_format_json_empty_count(report):
    data = json.loads(format_json(report))
    assert data["empty_count"] == report.empty_count


def test_format_json_entries_have_required_fields(report):
    data = json.loads(format_json(report))
    for entry in data["entries"]:
        assert "key" in entry
        assert "category" in entry
        assert "is_empty" in entry
        assert "value_length" in entry


def test_format_csv_parses_correctly(report):
    output = format_csv(report)
    reader = csv.DictReader(io.StringIO(output))
    rows = list(reader)
    assert len(rows) == report.total
    assert "key" in reader.fieldnames
    assert "category" in reader.fieldnames


def test_format_csv_empty_env():
    empty_report = profile_env({})
    output = format_csv(empty_report)
    reader = csv.DictReader(io.StringIO(output))
    rows = list(reader)
    assert rows == []
