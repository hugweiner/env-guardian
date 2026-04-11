"""Tests for env_guardian.map_formatter."""

import json
import csv
import io
import pytest

from env_guardian.mapper import map_env
from env_guardian.map_formatter import format_text, format_json, format_csv


@pytest.fixture()
def env():
    return {
        "OLD_HOST": "localhost",
        "OLD_PORT": "5432",
        "EXTRA_KEY": "value",
    }


@pytest.fixture()
def report(env):
    return map_env(env, {"OLD_HOST": "HOST", "OLD_PORT": "PORT", "MISSING": "GONE"})


def test_format_text_contains_header(report):
    output = format_text(report)
    assert "Key Mapping Report" in output


def test_format_text_contains_mapped_keys(report):
    output = format_text(report)
    assert "OLD_HOST" in output
    assert "HOST" in output


def test_format_text_contains_summary(report):
    output = format_text(report)
    assert "mapped" in output
    assert "skipped" in output


def test_format_text_shows_skipped_entry(report):
    output = format_text(report)
    assert "SKIP" in output
    assert "MISSING" in output


def test_format_json_valid_json(report):
    output = format_json(report)
    data = json.loads(output)
    assert "entries" in data
    assert "summary" in data


def test_format_json_summary_counts(report):
    output = format_json(report)
    data = json.loads(output)
    assert data["summary"]["mapped"] == 2
    assert data["summary"]["skipped"] == 1


def test_format_json_entries_contain_source_and_target(report):
    output = format_json(report)
    data = json.loads(output)
    keys = {e["source_key"] for e in data["entries"]}
    assert "OLD_HOST" in keys
    assert "OLD_PORT" in keys


def test_format_json_skipped_entry_has_null_value(report):
    output = format_json(report)
    data = json.loads(output)
    skipped = next(e for e in data["entries"] if e["skipped"])
    assert skipped["value"] is None


def test_format_csv_parseable(report):
    output = format_csv(report)
    reader = csv.DictReader(io.StringIO(output))
    rows = list(reader)
    assert len(rows) == len(report.entries)


def test_format_csv_has_correct_columns(report):
    output = format_csv(report)
    reader = csv.DictReader(io.StringIO(output))
    assert reader.fieldnames == ["source_key", "target_key", "value", "skipped", "skip_reason"]
