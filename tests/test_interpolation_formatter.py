"""Tests for env_guardian.interpolation_formatter."""
import json
import pytest
from env_guardian.interpolator import interpolate, InterpolationResult, InterpolationWarning
from env_guardian.interpolation_formatter import format_text, format_json, format_csv


@pytest.fixture
def clean_result() -> InterpolationResult:
    return interpolate({"APP": "guardian", "VERSION": "1.0"})


@pytest.fixture
def result_with_warnings() -> InterpolationResult:
    return interpolate({"URL": "http://${MISSING}", "PATH": "${BASE}/bin"})


# --- format_text ---

def test_format_text_clean_shows_no_warnings(clean_result):
    out = format_text(clean_result)
    assert "No unresolved" in out


def test_format_text_shows_warning_count(result_with_warnings):
    out = format_text(result_with_warnings)
    assert "Warnings" in out
    assert "2" in out


def test_format_text_contains_header(clean_result):
    assert "Interpolation Result" in format_text(clean_result)


def test_format_text_shows_resolved_key_count(clean_result):
    out = format_text(clean_result)
    assert "2" in out


# --- format_json ---

def test_format_json_is_valid_json(clean_result):
    out = format_json(clean_result)
    parsed = json.loads(out)
    assert "resolved_env" in parsed
    assert "warnings" in parsed
    assert "is_clean" in parsed


def test_format_json_clean_flag_true(clean_result):
    parsed = json.loads(format_json(clean_result))
    assert parsed["is_clean"] is True


def test_format_json_warnings_populated(result_with_warnings):
    parsed = json.loads(format_json(result_with_warnings))
    assert len(parsed["warnings"]) == 2
    keys = {w["key"] for w in parsed["warnings"]}
    assert "URL" in keys
    assert "PATH" in keys


def test_format_json_resolved_env_contains_keys(clean_result):
    parsed = json.loads(format_json(clean_result))
    assert "APP" in parsed["resolved_env"]


# --- format_csv ---

def test_format_csv_has_header(result_with_warnings):
    out = format_csv(result_with_warnings)
    assert out.startswith("key,ref,message")


def test_format_csv_clean_has_no_data_rows(clean_result):
    out = format_csv(clean_result)
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 1  # header only


def test_format_csv_rows_match_warnings(result_with_warnings):
    out = format_csv(result_with_warnings)
    lines = out.strip().splitlines()
    assert len(lines) == 3  # header + 2 warnings
