"""Tests for env_guardian.snapshotter."""
import pytest

from env_guardian.snapshotter import (
    Snapshot,
    SnapshotDiff,
    diff_snapshots,
    snapshot_from_dict,
    snapshot_to_dict,
    take_snapshot,
)


BASE_ENV = {"APP_ENV": "production", "DEBUG": "false", "PORT": "8080"}


def test_take_snapshot_captures_all_keys():
    snap = take_snapshot(BASE_ENV, label="v1")
    assert set(snap.entries.keys()) == set(BASE_ENV.keys())


def test_take_snapshot_stores_values():
    snap = take_snapshot(BASE_ENV, label="v1")
    assert snap.env == BASE_ENV


def test_take_snapshot_label_stored():
    snap = take_snapshot(BASE_ENV, label="release-1")
    assert snap.label == "release-1"


def test_clean_diff_is_clean():
    snap1 = take_snapshot(BASE_ENV, label="a")
    snap2 = take_snapshot(BASE_ENV, label="b")
    diff = diff_snapshots(snap1, snap2)
    assert diff.is_clean()


def test_added_key_detected():
    snap1 = take_snapshot(BASE_ENV, label="a")
    new_env = {**BASE_ENV, "NEW_KEY": "value"}
    snap2 = take_snapshot(new_env, label="b")
    diff = diff_snapshots(snap1, snap2)
    assert "NEW_KEY" in diff.added
    assert diff.added["NEW_KEY"] == "value"


def test_removed_key_detected():
    snap1 = take_snapshot(BASE_ENV, label="a")
    reduced = {k: v for k, v in BASE_ENV.items() if k != "DEBUG"}
    snap2 = take_snapshot(reduced, label="b")
    diff = diff_snapshots(snap1, snap2)
    assert "DEBUG" in diff.removed


def test_changed_key_detected():
    snap1 = take_snapshot(BASE_ENV, label="a")
    modified = {**BASE_ENV, "PORT": "9090"}
    snap2 = take_snapshot(modified, label="b")
    diff = diff_snapshots(snap1, snap2)
    assert "PORT" in diff.changed
    assert diff.changed["PORT"] == ("8080", "9090")


def test_diff_summary_no_changes():
    snap = take_snapshot(BASE_ENV, label="x")
    diff = diff_snapshots(snap, snap)
    assert diff.summary() == "no changes"


def test_diff_summary_with_changes():
    snap1 = take_snapshot(BASE_ENV, label="a")
    snap2 = take_snapshot({"APP_ENV": "staging", "NEW": "1"}, label="b")
    diff = diff_snapshots(snap1, snap2)
    summary = diff.summary()
    assert "added" in summary
    assert "removed" in summary
    assert "changed" in summary


def test_snapshot_round_trip_serialization():
    snap = take_snapshot(BASE_ENV, label="rt")
    data = snapshot_to_dict(snap)
    restored = snapshot_from_dict(data)
    assert restored.label == snap.label
    assert restored.env == snap.env
    assert restored.created_at == snap.created_at


def test_snapshot_keys_sorted():
    snap = take_snapshot(BASE_ENV, label="s")
    assert snap.keys() == sorted(BASE_ENV.keys())
