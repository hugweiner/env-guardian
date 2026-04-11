"""Tests for env_guardian.group_formatter."""
import csv
import io
import json

import pytest

from env_guardian.group_formatter import format_csv, format_json, format_text
from env_guardian.grouper import group_env


@pytest.fixture()
def report():
    env = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_HOST": "redis",
        "REDIS_PORT": "6379",
        "DEBUG": "true",
    }
    return group_env(env, min_group_size=2)


@pytest.fixture()
def empty_report():
    return group_env({})


def test_format_text_contains_header(report):
    out = format_text(report)
    assert "ENV VARIABLE GROUPS" in out


def test_format_text_contains_group_names(report):
    out = format_text(report)
    assert "[DB]" in out
    assert "[REDIS]" in out


def test_format_text_contains_all_keys(report):
    out = format_text(report)
    for key in ["DB_HOST", "DB_PORT", "REDIS_HOST", "REDIS_PORT", "DEBUG"]:
        assert key in out


def test_format_text_shows_summary(report):
    out = format_text(report)
    assert "group" in out


def test_format_text_empty_report(empty_report):
    out = format_text(empty_report)
    assert "0 group" in out


def test_format_json_valid_json(report):
    out = format_json(report)
    data = json.loads(out)
    assert "groups" in data
    assert "ungrouped" in data
    assert "summary" in data


def test_format_json_groups_present(report):
    data = json.loads(format_json(report))
    assert "DB" in data["groups"]
    assert "REDIS" in data["groups"]


def test_format_json_ungrouped_contains_debug(report):
    data = json.loads(format_json(report))
    ungrouped_keys = [e["key"] for e in data["ungrouped"]]
    assert "DEBUG" in ungrouped_keys


def test_format_csv_has_header(report):
    out = format_csv(report)
    reader = csv.reader(io.StringIO(out))
    header = next(reader)
    assert header == ["key", "value", "group", "suffix"]


def test_format_csv_row_count(report):
    out = format_csv(report)
    reader = csv.reader(io.StringIO(out))
    rows = list(reader)
    # header + 5 data rows
    assert len(rows) == 6


def test_format_csv_group_column_correct(report):
    out = format_csv(report)
    reader = csv.reader(io.StringIO(out))
    next(reader)  # skip header
    groups = {row[0]: row[2] for row in reader}
    assert groups["DB_HOST"] == "DB"
    assert groups["REDIS_PORT"] == "REDIS"
