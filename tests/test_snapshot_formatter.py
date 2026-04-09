"""Tests for env_guardian.snapshot_formatter."""
import json
import csv
import io

import pytest

from env_guardian.snapshotter import SnapshotDiff, diff_snapshots, take_snapshot
from env_guardian.snapshot_formatter import format_csv, format_json, format_text


@pytest.fixture()
def clean_diff() -> SnapshotDiff:
    env = {"A": "1", "B": "2"}
    s1 = take_snapshot(env, label="old")
    s2 = take_snapshot(env, label="new")
    return diff_snapshots(s1, s2)


@pytest.fixture()
def rich_diff() -> SnapshotDiff:
    old_env = {"A": "1", "B": "2", "C": "3"}
    new_env = {"A": "99", "B": "2", "D": "4"}
    s1 = take_snapshot(old_env, label="old")
    s2 = take_snapshot(new_env, label="new")
    return diff_snapshots(s1, s2)


def test_format_text_clean_shows_no_differences(clean_diff):
    out = format_text(clean_diff)
    assert "no differences" in out


def test_format_text_contains_header(rich_diff):
    out = format_text(rich_diff, old_label="v1", new_label="v2")
    assert "v1" in out
    assert "v2" in out


def test_format_text_shows_added_key(rich_diff):
    out = format_text(rich_diff)
    assert "D" in out
    assert "ADDED" in out


def test_format_text_shows_removed_key(rich_diff):
    out = format_text(rich_diff)
    assert "C" in out
    assert "REMOVED" in out


def test_format_text_shows_changed_key(rich_diff):
    out = format_text(rich_diff)
    assert "A" in out
    assert "CHANGED" in out


def test_format_json_valid_json(rich_diff):
    out = format_json(rich_diff)
    data = json.loads(out)
    assert "added" in data
    assert "removed" in data
    assert "changed" in data
    assert "summary" in data


def test_format_json_changed_has_old_and_new(rich_diff):
    data = json.loads(format_json(rich_diff))
    assert "A" in data["changed"]
    assert data["changed"]["A"]["old"] == "1"
    assert data["changed"]["A"]["new"] == "99"


def test_format_csv_has_header(rich_diff):
    out = format_csv(rich_diff)
    reader = csv.reader(io.StringIO(out))
    header = next(reader)
    assert header == ["change_type", "key", "old_value", "new_value"]


def test_format_csv_rows_for_all_changes(rich_diff):
    out = format_csv(rich_diff)
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    change_types = {r["change_type"] for r in rows}
    assert "added" in change_types
    assert "removed" in change_types
    assert "changed" in change_types
