"""Tests for env_guardian.hasher and env_guardian.hash_formatter."""
from __future__ import annotations

import hashlib
import json

import pytest

from env_guardian.hasher import hash_env
from env_guardian.hash_formatter import format_csv, format_json, format_text


@pytest.fixture()
def simple_env():
    return {"API_KEY": "secret123", "DEBUG": "true", "PORT": "8080"}


def test_hash_env_returns_report(simple_env):
    report = hash_env(simple_env)
    assert report is not None


def test_all_keys_present_in_report(simple_env):
    report = hash_env(simple_env)
    keys = {e.key for e in report.entries}
    assert keys == set(simple_env.keys())


def test_digest_matches_sha256(simple_env):
    report = hash_env(simple_env, algorithm="sha256")
    for entry in report.entries:
        expected = hashlib.sha256(simple_env[entry.key].encode()).hexdigest()
        assert entry.digest == expected


def test_md5_algorithm_used(simple_env):
    report = hash_env(simple_env, algorithm="md5")
    for entry in report.entries:
        expected = hashlib.md5(simple_env[entry.key].encode()).hexdigest()
        assert entry.digest == expected


def test_digest_for_known_key(simple_env):
    report = hash_env(simple_env)
    digest = report.digest_for("PORT")
    expected = hashlib.sha256(b"8080").hexdigest()
    assert digest == expected


def test_digest_for_missing_key_returns_none(simple_env):
    report = hash_env(simple_env)
    assert report.digest_for("NONEXISTENT") is None


def test_as_dict_returns_all_keys(simple_env):
    report = hash_env(simple_env)
    d = report.as_dict()
    assert set(d.keys()) == set(simple_env.keys())


def test_mismatches_detects_changed_value():
    env_a = {"KEY": "value1"}
    env_b = {"KEY": "value2"}
    report_a = hash_env(env_a)
    report_b = hash_env(env_b)
    assert "KEY" in report_a.mismatches(report_b)


def test_mismatches_empty_when_identical(simple_env):
    r1 = hash_env(simple_env)
    r2 = hash_env(simple_env)
    assert r1.mismatches(r2) == []


def test_summary_contains_algorithm(simple_env):
    report = hash_env(simple_env, algorithm="sha1")
    assert "sha1" in report.summary()


def test_format_text_contains_header(simple_env):
    report = hash_env(simple_env)
    text = format_text(report)
    assert "Hash Report" in text


def test_format_text_contains_all_keys(simple_env):
    report = hash_env(simple_env)
    text = format_text(report)
    for key in simple_env:
        assert key in text


def test_format_json_valid_json(simple_env):
    report = hash_env(simple_env)
    data = json.loads(format_json(report))
    assert "entries" in data
    assert data["algorithm"] == "sha256"


def test_format_csv_has_header(simple_env):
    report = hash_env(simple_env)
    csv_text = format_csv(report)
    assert csv_text.startswith("key,algorithm,digest")


def test_format_csv_contains_all_keys(simple_env):
    report = hash_env(simple_env)
    csv_text = format_csv(report)
    for key in simple_env:
        assert key in csv_text
