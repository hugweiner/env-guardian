"""Tests for env_guardian.split_formatter."""
import csv
import io
import json

import pytest

from env_guardian.splitter import split_env
from env_guardian.split_formatter import format_csv, format_json, format_text


@pytest.fixture
def env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_URL": "redis://localhost",
        "APP_ENV": "production",
    }


@pytest.fixture
def report(env):
    return split_env(env, rules={"db": "DB_", "redis": "REDIS_"})


def test_format_text_contains_header(report):
    text = format_text(report)
    assert "Env Split Report" in text


def test_format_text_contains_bucket_names(report):
    text = format_text(report)
    assert "[db]" in text
    assert "[redis]" in text
    assert "[ungrouped]" in text


def test_format_text_contains_all_keys(report, env):
    text = format_text(report)
    for key in env:
        assert key in text


def test_format_text_contains_summary(report):
    text = format_text(report)
    assert "bucket" in text


def test_format_json_valid_json(report):
    raw = format_json(report)
    data = json.loads(raw)
    assert "buckets" in data
    assert "summary" in data


def test_format_json_buckets_present(report):
    data = json.loads(format_json(report))
    assert "db" in data["buckets"]
    assert "redis" in data["buckets"]


def test_format_json_db_keys_correct(report):
    data = json.loads(format_json(report))
    assert data["buckets"]["db"] == {"DB_HOST": "localhost", "DB_PORT": "5432"}


def test_format_csv_has_header(report):
    raw = format_csv(report)
    reader = csv.reader(io.StringIO(raw))
    header = next(reader)
    assert header == ["bucket", "key", "value"]


def test_format_csv_row_count_matches_env(report, env):
    raw = format_csv(report)
    rows = list(csv.reader(io.StringIO(raw)))
    # header + one row per key
    assert len(rows) == len(env) + 1
