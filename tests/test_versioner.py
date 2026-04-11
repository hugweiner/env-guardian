"""Tests for env_guardian.versioner and env_guardian.version_formatter."""
import json

import pytest

from env_guardian.versioner import (
    SchemaDrift,
    VersionReport,
    diff_versions,
    stamp_version,
)
from env_guardian.version_formatter import format_csv, format_json, format_text


@pytest.fixture()
def empty_report() -> VersionReport:
    return VersionReport()


@pytest.fixture()
def base_env() -> dict:
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET_KEY": "abc"}


# --- versioner ---

def test_stamp_version_adds_entry(empty_report, base_env):
    stamp_version(empty_report, base_env, label="initial")
    assert empty_report.version_count() == 1


def test_first_version_number_is_one(empty_report, base_env):
    entry = stamp_version(empty_report, base_env)
    assert entry.version == 1


def test_second_version_number_increments(empty_report, base_env):
    stamp_version(empty_report, base_env)
    entry = stamp_version(empty_report, base_env, label="v2")
    assert entry.version == 2


def test_label_stored(empty_report, base_env):
    entry = stamp_version(empty_report, base_env, label="release-1")
    assert entry.label == "release-1"


def test_default_label_uses_version_number(empty_report, base_env):
    entry = stamp_version(empty_report, base_env)
    assert entry.label == "v1"


def test_keys_are_sorted(empty_report, base_env):
    entry = stamp_version(empty_report, base_env)
    assert entry.keys == sorted(base_env.keys())


def test_schema_hash_is_deterministic(base_env):
    r1, r2 = VersionReport(), VersionReport()
    e1 = stamp_version(r1, base_env)
    e2 = stamp_version(r2, base_env)
    assert e1.schema_hash == e2.schema_hash


def test_schema_hash_differs_when_keys_differ(base_env):
    r = VersionReport()
    e1 = stamp_version(r, base_env)
    new_env = {**base_env, "EXTRA": "val"}
    e2 = stamp_version(r, new_env)
    assert e1.schema_hash != e2.schema_hash


def test_get_returns_correct_entry(empty_report, base_env):
    stamp_version(empty_report, base_env)
    stamp_version(empty_report, base_env)
    assert empty_report.get(2).version == 2


def test_get_missing_version_returns_none(empty_report):
    assert empty_report.get(99) is None


def test_diff_versions_no_drift(base_env):
    r = VersionReport()
    e1 = stamp_version(r, base_env)
    e2 = stamp_version(r, base_env)
    drift = diff_versions(e1, e2)
    assert not drift.has_drift


def test_diff_versions_added_key(base_env):
    r = VersionReport()
    e1 = stamp_version(r, base_env)
    e2 = stamp_version(r, {**base_env, "NEW_KEY": "x"})
    drift = diff_versions(e1, e2)
    assert "NEW_KEY" in drift.added
    assert drift.has_drift


def test_diff_versions_removed_key(base_env):
    r = VersionReport()
    reduced = {k: v for k, v in base_env.items() if k != "SECRET_KEY"}
    e1 = stamp_version(r, base_env)
    e2 = stamp_version(r, reduced)
    drift = diff_versions(e1, e2)
    assert "SECRET_KEY" in drift.removed


def test_drift_summary_no_drift():
    d = SchemaDrift()
    assert d.summary() == "No schema drift detected."


def test_drift_summary_with_changes():
    d = SchemaDrift(added=["A"], removed=["B", "C"])
    assert "+1 added" in d.summary()
    assert "-2 removed" in d.summary()


# --- formatters ---

def test_format_text_contains_header(empty_report, base_env):
    stamp_version(empty_report, base_env)
    out = format_text(empty_report)
    assert "Version History" in out


def test_format_text_shows_version_count(empty_report, base_env):
    stamp_version(empty_report, base_env)
    stamp_version(empty_report, base_env)
    out = format_text(empty_report)
    assert "Total versions: 2" in out


def test_format_text_with_drift(empty_report, base_env):
    e1 = stamp_version(empty_report, base_env)
    e2 = stamp_version(empty_report, {**base_env, "EXTRA": "1"})
    drift = diff_versions(e1, e2)
    out = format_text(empty_report, drift=drift)
    assert "Schema Drift" in out
    assert "EXTRA" in out


def test_format_json_valid(empty_report, base_env):
    stamp_version(empty_report, base_env)
    data = json.loads(format_json(empty_report))
    assert "versions" in data
    assert data["versions"][0]["version"] == 1


def test_format_json_includes_drift(empty_report, base_env):
    e1 = stamp_version(empty_report, base_env)
    e2 = stamp_version(empty_report, {**base_env, "NEW": "v"})
    drift = diff_versions(e1, e2)
    data = json.loads(format_json(empty_report, drift=drift))
    assert data["drift"]["added"] == ["NEW"]


def test_format_csv_contains_header(empty_report, base_env):
    stamp_version(empty_report, base_env)
    out = format_csv(empty_report)
    assert "version" in out
    assert "schema_hash" in out


def test_format_csv_row_count(empty_report, base_env):
    stamp_version(empty_report, base_env)
    stamp_version(empty_report, base_env)
    rows = [r for r in format_csv(empty_report).strip().splitlines() if r]
    assert len(rows) == 3  # header + 2 data rows
