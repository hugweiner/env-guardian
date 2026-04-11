"""Tests for env_guardian.cast_formatter."""
import csv
import io
import json

import pytest

from env_guardian.caster import cast_env
from env_guardian.cast_formatter import format_csv, format_json, format_text


@pytest.fixture()
def report():
    env = {"PORT": "8080", "DEBUG": "true", "APP_NAME": "guardian"}
    return cast_env(env)


def test_format_text_contains_header(report):
    out = format_text(report)
    assert "Cast Report" in out


def test_format_text_contains_all_keys(report):
    out = format_text(report)
    assert "PORT" in out
    assert "DEBUG" in out
    assert "APP_NAME" in out


def test_format_text_shows_summary(report):
    out = format_text(report)
    assert "keys cast" in out


def test_format_text_empty_report():
    from env_guardian.caster import CastReport

    out = format_text(CastReport())
    assert "No entries" in out


def test_format_json_valid_json(report):
    out = format_json(report)
    data = json.loads(out)
    assert isinstance(data, list)
    assert len(data) == 3


def test_format_json_contains_expected_fields(report):
    out = format_json(report)
    data = json.loads(out)
    keys_in_output = {item["key"] for item in data}
    assert "PORT" in keys_in_output
    first = next(d for d in data if d["key"] == "PORT")
    assert "raw_value" in first
    assert "cast_value" in first
    assert "inferred_type" in first


def test_format_json_int_type(report):
    data = json.loads(format_json(report))
    port_entry = next(d for d in data if d["key"] == "PORT")
    assert port_entry["inferred_type"] == "int"
    assert port_entry["cast_value"] == 8080


def test_format_csv_has_header(report):
    out = format_csv(report)
    reader = csv.reader(io.StringIO(out))
    header = next(reader)
    assert header == ["key", "raw_value", "cast_value", "inferred_type"]


def test_format_csv_row_count(report):
    out = format_csv(report)
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 4  # header + 3 entries


def test_format_csv_sorted_by_key(report):
    out = format_csv(report)
    rows = list(csv.reader(io.StringIO(out)))
    data_rows = rows[1:]
    keys = [r[0] for r in data_rows]
    assert keys == sorted(keys)
