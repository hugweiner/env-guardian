"""Tests for env_guardian.splitter and env_guardian.split_formatter."""

import json

import pytest

from env_guardian.splitter import split_env
from env_guardian.split_formatter import format_csv, format_json, format_text


@pytest.fixture()
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_URL": "redis://localhost",
        "REDIS_PASSWORD": "secret",
        "APP_NAME": "guardian",
        "DEBUG": "true",
    }


def test_split_returns_report(mixed_env):
    report = split_env(mixed_env, prefixes=["DB", "REDIS"])
    assert report is not None


def test_db_keys_in_db_bucket(mixed_env):
    report = split_env(mixed_env, prefixes=["DB", "REDIS"])
    bucket = report.get_bucket("db")
    assert "DB_HOST" in bucket
    assert "DB_PORT" in bucket


def test_redis_keys_in_redis_bucket(mixed_env):
    report = split_env(mixed_env, prefixes=["DB", "REDIS"])
    bucket = report.get_bucket("redis")
    assert "REDIS_URL" in bucket
    assert "REDIS_PASSWORD" in bucket


def test_unmatched_keys_go_to_ungrouped(mixed_env):
    report = split_env(mixed_env, prefixes=["DB", "REDIS"])
    ungrouped = report.get_bucket("ungrouped")
    assert "APP_NAME" in ungrouped
    assert "DEBUG" in ungrouped


def test_include_ungrouped_false_drops_unmatched(mixed_env):
    report = split_env(mixed_env, prefixes=["DB"], include_ungrouped=False)
    assert "ungrouped" not in report.bucket_names()


def test_bucket_names_sorted(mixed_env):
    report = split_env(mixed_env, prefixes=["REDIS", "DB"])
    names = report.bucket_names()
    assert names == sorted(names)


def test_bucket_count(mixed_env):
    report = split_env(mixed_env, prefixes=["DB", "REDIS"])
    # db, redis, ungrouped
    assert report.bucket_count() == 3


def test_summary_contains_counts(mixed_env):
    report = split_env(mixed_env, prefixes=["DB", "REDIS"])
    summary = report.summary()
    assert "6" in summary
    assert "3" in summary


def test_no_prefixes_all_ungrouped(mixed_env):
    report = split_env(mixed_env)
    assert report.bucket_names() == ["ungrouped"]
    assert len(report.get_bucket("ungrouped")) == len(mixed_env)


def test_format_text_contains_header(mixed_env):
    report = split_env(mixed_env, prefixes=["DB"])
    text = format_text(report)
    assert "ENV SPLIT REPORT" in text


def test_format_text_contains_bucket_name(mixed_env):
    report = split_env(mixed_env, prefixes=["DB"])
    text = format_text(report)
    assert "[db]" in text


def test_format_json_valid(mixed_env):
    report = split_env(mixed_env, prefixes=["DB", "REDIS"])
    data = json.loads(format_json(report))
    assert "buckets" in data
    assert "db" in data["buckets"]
    assert "redis" in data["buckets"]


def test_format_csv_contains_header(mixed_env):
    report = split_env(mixed_env, prefixes=["DB"])
    csv_text = format_csv(report)
    assert "bucket,key,value" in csv_text


def test_format_csv_contains_entries(mixed_env):
    report = split_env(mixed_env, prefixes=["DB"])
    csv_text = format_csv(report)
    assert "DB_HOST" in csv_text
    assert "DB_PORT" in csv_text
