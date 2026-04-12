"""Tests for env_guardian.compactor and env_guardian.compact_formatter."""
import json

import pytest

from env_guardian.compact_formatter import format_csv, format_json, format_text
from env_guardian.compactor import CompactReport, compact_env


# ---------------------------------------------------------------------------
# compact_env
# ---------------------------------------------------------------------------

def test_clean_env_produces_no_warnings():
    env = {"KEY": "value", "PORT": "8080"}
    report = compact_env(env)
    assert report.is_clean()
    assert report.removed_count() == 0


def test_clean_env_retains_all_keys():
    env = {"A": "1", "B": "2"}
    report = compact_env(env)
    assert report.compacted_env == env


def test_empty_value_is_removed():
    env = {"PRESENT": "ok", "EMPTY": ""}
    report = compact_env(env)
    assert "EMPTY" not in report.compacted_env
    assert "PRESENT" in report.compacted_env


def test_whitespace_only_value_removed_by_default():
    env = {"BLANK": "   ", "REAL": "data"}
    report = compact_env(env)
    assert "BLANK" not in report.compacted_env


def test_whitespace_only_retained_when_strip_false():
    env = {"BLANK": "   "}
    report = compact_env(env, strip=False)
    assert report.is_clean()
    assert "BLANK" in report.compacted_env


def test_warning_contains_original_value():
    env = {"KEY": ""}
    report = compact_env(env)
    assert report.warnings[0].original_value == ""


def test_warning_key_matches():
    env = {"GONE": ""}
    report = compact_env(env)
    assert report.warnings[0].key == "GONE"


def test_removed_count_correct():
    env = {"A": "", "B": " ", "C": "ok"}
    report = compact_env(env)
    assert report.removed_count() == 2


def test_summary_contains_counts():
    env = {"A": "", "B": "val"}
    report = compact_env(env)
    summary = report.summary()
    assert "1 removed" in summary
    assert "1 retained" in summary


# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------

def test_format_text_clean_shows_no_removals():
    env = {"X": "1"}
    report = compact_env(env)
    text = format_text(report)
    assert "Nothing removed" in text


def test_format_text_shows_removed_key():
    env = {"EMPTY_KEY": ""}
    report = compact_env(env)
    text = format_text(report)
    assert "EMPTY_KEY" in text


# ---------------------------------------------------------------------------
# format_json
# ---------------------------------------------------------------------------

def test_format_json_valid_json():
    report = compact_env({"A": "", "B": "ok"})
    payload = json.loads(format_json(report))
    assert "removed" in payload
    assert "compacted_env" in payload


def test_format_json_removed_count():
    report = compact_env({"A": "", "B": "", "C": "keep"})
    payload = json.loads(format_json(report))
    assert payload["removed_count"] == 2


# ---------------------------------------------------------------------------
# format_csv
# ---------------------------------------------------------------------------

def test_format_csv_contains_header():
    report = compact_env({})
    csv_out = format_csv(report)
    assert "key" in csv_out
    assert "status" in csv_out


def test_format_csv_removed_row_status():
    report = compact_env({"GONE": ""})
    csv_out = format_csv(report)
    assert "removed" in csv_out


def test_format_csv_retained_row_status():
    report = compact_env({"KEPT": "yes"})
    csv_out = format_csv(report)
    assert "retained" in csv_out
