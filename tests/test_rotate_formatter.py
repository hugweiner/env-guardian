"""Tests for env_guardian.rotate_formatter."""
from __future__ import annotations

import json

import pytest

from env_guardian.rotator import rotate_env
from env_guardian.rotate_formatter import format_csv, format_json, format_text


@pytest.fixture()
def clean_report():
    return rotate_env({"API_KEY": "secret", "DB_URL": "postgres://localhost/db"})


@pytest.fixture()
def stale_report():
    return rotate_env(
        {"TOKEN_OLD": "abc", "PASS_BACKUP": "xyz", "ACTIVE": "yes"}
    )


def test_format_text_contains_header(clean_report):
    out = format_text(clean_report)
    assert "Key Rotation Report" in out


def test_format_text_clean_shows_no_stale(clean_report):
    out = format_text(clean_report)
    assert "No stale keys detected" in out


def test_format_text_shows_stale_count(stale_report):
    out = format_text(stale_report)
    assert "Stale keys: 2" in out


def test_format_text_stale_tag_present(stale_report):
    out = format_text(stale_report)
    assert "[STALE]" in out


def test_format_text_ok_tag_present(stale_report):
    out = format_text(stale_report)
    assert "[ok]" in out


def test_format_text_contains_summary(clean_report):
    out = format_text(clean_report)
    assert "processed" in out


def test_format_json_valid_json(clean_report):
    out = format_json(clean_report)
    data = json.loads(out)
    assert "entries" in data
    assert "stale_count" in data


def test_format_json_stale_count(stale_report):
    data = json.loads(format_json(stale_report))
    assert data["stale_count"] == 2


def test_format_json_entries_have_required_fields(clean_report):
    data = json.loads(format_json(clean_report))
    for entry in data["entries"]:
        assert "key" in entry
        assert "rotated_key" in entry
        assert "stale" in entry
        assert "reason" in entry


def test_format_csv_header_row(clean_report):
    out = format_csv(clean_report)
    first_line = out.splitlines()[0]
    assert "key" in first_line
    assert "rotated_key" in first_line


def test_format_csv_row_count(clean_report):
    out = format_csv(clean_report)
    rows = out.strip().splitlines()
    # header + 2 entries
    assert len(rows) == 3
