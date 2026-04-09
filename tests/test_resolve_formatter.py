"""Tests for env_guardian.resolve_formatter."""
import csv
import io
import json

import pytest

from env_guardian.resolve_formatter import format_csv, format_json, format_text
from env_guardian.resolver import resolve_layers


@pytest.fixture
def report():
    return resolve_layers(
        [
            ("base", {"APP_ENV": "dev", "DB_URL": "localhost"}),
            ("prod", {"APP_ENV": "production", "SECRET_KEY": "s3cr3t"}),
        ]
    )


def test_format_text_contains_header(report):
    out = format_text(report)
    assert "Resolved Environment Variables" in out


def test_format_text_contains_all_keys(report):
    out = format_text(report)
    assert "APP_ENV" in out
    assert "DB_URL" in out
    assert "SECRET_KEY" in out


def test_format_text_marks_overridden_key(report):
    out = format_text(report)
    # APP_ENV exists in both layers so it should be flagged
    assert "[overridden]" in out


def test_format_text_contains_summary(report):
    out = format_text(report)
    assert "Resolved" in out
    assert "layer" in out


def test_format_json_valid_json(report):
    out = format_json(report)
    data = json.loads(out)
    assert "entries" in data
    assert "layers" in data
    assert "summary" in data


def test_format_json_entries_have_required_fields(report):
    data = json.loads(format_json(report))
    for entry in data["entries"]:
        assert "key" in entry
        assert "value" in entry
        assert "source" in entry
        assert "overridden" in entry


def test_format_json_overridden_flag_correct(report):
    data = json.loads(format_json(report))
    by_key = {e["key"]: e for e in data["entries"]}
    assert by_key["APP_ENV"]["overridden"] is True
    assert by_key["DB_URL"]["overridden"] is False


def test_format_csv_parseable(report):
    out = format_csv(report)
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert len(rows) == 3  # APP_ENV, DB_URL, SECRET_KEY


def test_format_csv_has_correct_columns(report):
    out = format_csv(report)
    reader = csv.DictReader(io.StringIO(out))
    assert reader.fieldnames == ["key", "value", "source", "overridden"]
