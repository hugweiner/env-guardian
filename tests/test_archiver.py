"""Tests for env_guardian.archiver and env_guardian.archive_formatter."""
from __future__ import annotations

import json
import os
import pytest

from env_guardian.archiver import archive_env, load_archive, ArchiveEntry, ArchiveStore
from env_guardian.archive_formatter import format_text, format_json, format_csv


FIXED_TS = "2024-01-01T00:00:00+00:00"
FIXED_TS2 = "2024-01-02T00:00:00+00:00"


@pytest.fixture()
def archive_path(tmp_path):
    return str(tmp_path / "test.archive.jsonl")


# ------------------------------------------------------------------ archiver

def test_archive_env_creates_file(archive_path):
    archive_env({"A": "1"}, label="prod", path=archive_path, timestamp=FIXED_TS)
    assert os.path.exists(archive_path)


def test_archive_env_returns_entry(archive_path):
    entry = archive_env({"A": "1"}, label="prod", path=archive_path, timestamp=FIXED_TS)
    assert isinstance(entry, ArchiveEntry)
    assert entry.label == "prod"
    assert entry.env == {"A": "1"}
    assert entry.timestamp == FIXED_TS


def test_archive_env_appends_multiple(archive_path):
    archive_env({"A": "1"}, label="prod", path=archive_path, timestamp=FIXED_TS)
    archive_env({"B": "2"}, label="staging", path=archive_path, timestamp=FIXED_TS2)
    store = load_archive(archive_path)
    assert store.count == 2


def test_load_archive_returns_store(archive_path):
    archive_env({"X": "y"}, label="dev", path=archive_path, timestamp=FIXED_TS)
    store = load_archive(archive_path)
    assert isinstance(store, ArchiveStore)


def test_load_archive_missing_file_returns_empty(archive_path):
    store = load_archive(archive_path + ".missing")
    assert store.count == 0


def test_load_archive_preserves_env(archive_path):
    env = {"FOO": "bar", "BAZ": "qux"}
    archive_env(env, label="test", path=archive_path, timestamp=FIXED_TS)
    store = load_archive(archive_path)
    assert store.entries[0].env == env


def test_store_latest_returns_last(archive_path):
    archive_env({"A": "1"}, label="first", path=archive_path, timestamp=FIXED_TS)
    archive_env({"B": "2"}, label="second", path=archive_path, timestamp=FIXED_TS2)
    store = load_archive(archive_path)
    assert store.latest().label == "second"


def test_store_by_label_filters(archive_path):
    archive_env({"A": "1"}, label="prod", path=archive_path, timestamp=FIXED_TS)
    archive_env({"B": "2"}, label="dev", path=archive_path, timestamp=FIXED_TS2)
    store = load_archive(archive_path)
    assert len(store.by_label("prod")) == 1
    assert store.by_label("prod")[0].env == {"A": "1"}


# ------------------------------------------------------------------ formatter

@pytest.fixture()
def populated_store(archive_path):
    archive_env({"DB_URL": "postgres://localhost/db"}, label="prod", path=archive_path, timestamp=FIXED_TS)
    archive_env({"DB_URL": "sqlite:///dev.db"}, label="dev", path=archive_path, timestamp=FIXED_TS2)
    return load_archive(archive_path)


def test_format_text_contains_header(populated_store):
    out = format_text(populated_store)
    assert "Archive" in out


def test_format_text_contains_labels(populated_store):
    out = format_text(populated_store)
    assert "prod" in out
    assert "dev" in out


def test_format_text_empty_store(archive_path):
    store = load_archive(archive_path)
    out = format_text(store)
    assert "(empty)" in out


def test_format_json_valid_json(populated_store):
    out = format_json(populated_store)
    data = json.loads(out)
    assert "archive" in data
    assert data["count"] == 2


def test_format_csv_has_header(populated_store):
    out = format_csv(populated_store)
    assert out.startswith("timestamp,label,key,value")


def test_format_csv_contains_keys(populated_store):
    out = format_csv(populated_store)
    assert "DB_URL" in out
