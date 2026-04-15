"""Tests for env_guardian.limit_formatter."""
import json
import pytest

from env_guardian.limiter import limit_env
from env_guardian.limit_formatter import format_text, format_json, format_csv


@pytest.fixture
def clean_report():
    return limit_env({"KEY": "hello", "OTHER": "world"}, min_length=3, max_length=10)


@pytest.fixture
def dirty_report():
    return limit_env(
        {"SHORT": "hi", "FINE": "hello", "TOOLONG": "x" * 50},
        min_length=4,
        max_length=20,
    )


def test_format_text_clean_shows_no_violations(clean_report):
    out = format_text(clean_report)
    assert "No violations" in out


def test_format_text_contains_header(dirty_report):
    out = format_text(dirty_report)
    assert "Limit Report" in out


def test_format_text_shows_violation_count(dirty_report):
    out = format_text(dirty_report)
    assert "2" in out


def test_format_text_shows_too_short(dirty_report):
    out = format_text(dirty_report)
    assert "TOO_SHORT" in out or "too_short" in out.lower()


def test_format_text_shows_too_long(dirty_report):
    out = format_text(dirty_report)
    assert "TOO_LONG" in out or "too_long" in out.lower()


def test_format_json_valid_json(dirty_report):
    out = format_json(dirty_report)
    data = json.loads(out)
    assert "violations" in data
    assert "violation_count" in data


def test_format_json_clean_flag(clean_report):
    data = json.loads(format_json(clean_report))
    assert data["clean"] is True


def test_format_json_dirty_flag(dirty_report):
    data = json.loads(format_json(dirty_report))
    assert data["clean"] is False


def test_format_csv_has_header(dirty_report):
    out = format_csv(dirty_report)
    assert "key" in out
    assert "kind" in out


def test_format_csv_contains_violation_key(dirty_report):
    out = format_csv(dirty_report)
    assert "SHORT" in out or "TOOLONG" in out
