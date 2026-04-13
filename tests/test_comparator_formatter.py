"""Tests for comparator_formatter."""
from __future__ import annotations

import json

import pytest

from env_guardian.comparator import compare_envs
from env_guardian.comparator_formatter import format_csv, format_json, format_text


@pytest.fixture()
def clean_diff():
    return compare_envs({"A": "1", "B": "2"}, {"A": "1", "B": "2"})


@pytest.fixture()
def dirty_diff():
    base = {"A": "1", "B": "2", "C": "3"}
    target = {"A": "changed", "B": "2", "D": "4"}
    return compare_envs(base, target)


# --- format_text ---

def test_format_text_clean_shows_no_differences(clean_diff):
    out = format_text(clean_diff)
    assert "No differences found." in out


def test_format_text_shows_header(dirty_diff):
    out = format_text(dirty_diff)
    assert "Environment Comparison" in out


def test_format_text_shows_missing_key(dirty_diff):
    out = format_text(dirty_diff)
    assert "Missing keys" in out
    assert "C" in out


def test_format_text_shows_extra_key(dirty_diff):
    out = format_text(dirty_diff)
    assert "Extra keys" in out
    assert "D" in out


def test_format_text_shows_mismatched_key(dirty_diff):
    out = format_text(dirty_diff)
    assert "Mismatched values" in out
    assert "A" in out


def test_format_text_shows_summary(dirty_diff):
    out = format_text(dirty_diff)
    assert "Summary" in out


# --- format_json ---

def test_format_json_is_valid_json(dirty_diff):
    out = format_json(dirty_diff)
    data = json.loads(out)
    assert isinstance(data, dict)


def test_format_json_clean_diff(clean_diff):
    data = json.loads(format_json(clean_diff))
    assert data["is_clean"] is True
    assert data["missing"] == []
    assert data["extra"] == []
    assert data["mismatched"] == []


def test_format_json_contains_missing_key(dirty_diff):
    data = json.loads(format_json(dirty_diff))
    assert "C" in data["missing"]


def test_format_json_contains_extra_key(dirty_diff):
    data = json.loads(format_json(dirty_diff))
    assert "D" in data["extra"]


# --- format_csv ---

def test_format_csv_has_header(dirty_diff):
    out = format_csv(dirty_diff)
    assert out.startswith("key,issue")


def test_format_csv_contains_missing_row(dirty_diff):
    out = format_csv(dirty_diff)
    assert "C,missing" in out


def test_format_csv_contains_extra_row(dirty_diff):
    out = format_csv(dirty_diff)
    assert "D,extra" in out


def test_format_csv_clean_has_only_header(clean_diff):
    lines = format_csv(clean_diff).strip().splitlines()
    assert len(lines) == 1
