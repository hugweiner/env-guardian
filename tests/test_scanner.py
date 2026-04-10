"""Tests for env_guardian.scanner and env_guardian.scan_formatter."""

import json

import pytest

from env_guardian.scanner import ScanHit, ScanReport, scan_env
from env_guardian.scan_formatter import format_csv, format_json, format_text


# ---------------------------------------------------------------------------
# scan_env tests
# ---------------------------------------------------------------------------

def test_clean_env_produces_no_hits():
    env = {"APP_NAME": "myapp", "DEBUG": "true", "PORT": "8080"}
    report = scan_env(env)
    assert report.is_clean
    assert report.hits == []


def test_hex_token_flagged_as_high():
    env = {"AUTH_TOKEN": "a3f1c2e4b5d6e7f8a3f1c2e4b5d6e7f8"}
    report = scan_env(env)
    assert not report.is_clean
    assert any(h.severity == "high" for h in report.hits)


def test_url_with_credentials_flagged_as_medium():
    env = {"DATABASE_URL": "https://user:s3cr3t@db.example.com/mydb"}
    report = scan_env(env)
    assert not report.is_clean
    hit = report.hits[0]
    assert hit.key == "DATABASE_URL"
    assert hit.severity in ("high", "medium")


def test_api_key_prefix_flagged_as_high():
    env = {"STRIPE_KEY": "sk_live_abcdef1234567890abcd"}
    report = scan_env(env)
    assert any(h.severity == "high" for h in report.hits)


def test_empty_value_skipped():
    env = {"SECRET_KEY": ""}
    report = scan_env(env)
    # Empty values should not produce hits
    assert report.is_clean


def test_by_severity_filters_correctly():
    env = {
        "TOKEN": "a3f1c2e4b5d6e7f8a3f1c2e4b5d6e7f8",
        "APP": "hello",
    }
    report = scan_env(env)
    highs = report.by_severity("high")
    assert all(h.severity == "high" for h in highs)


def test_summary_lists_counts():
    env = {"TOKEN": "a3f1c2e4b5d6e7f8a3f1c2e4b5d6e7f8"}
    report = scan_env(env)
    assert "hit" in report.summary()


def test_summary_clean():
    report = ScanReport()
    assert report.summary() == "No suspicious values detected."


def test_scan_hit_str_masks_value():
    hit = ScanHit(key="SECRET", value="supersecretvalue", severity="high", reason="test")
    s = str(hit)
    assert "supe****" in s
    assert "supersecretvalue" not in s


# ---------------------------------------------------------------------------
# formatter tests
# ---------------------------------------------------------------------------

@pytest.fixture
def report_with_hits():
    report = ScanReport()
    report.add(ScanHit(key="API_KEY", value="abc1234567890xyz", severity="high", reason="Hex token"))
    report.add(ScanHit(key="DB_PASS", value="weakpass", severity="medium", reason="Key name hint"))
    return report


def test_format_text_clean():
    report = ScanReport()
    out = format_text(report)
    assert "No suspicious" in out


def test_format_text_with_hits(report_with_hits):
    out = format_text(report_with_hits)
    assert "API_KEY" in out
    assert "DB_PASS" in out
    assert "HIGH" in out


def test_format_json_valid(report_with_hits):
    out = format_json(report_with_hits)
    data = json.loads(out)
    assert "hits" in data
    assert data["clean"] is False
    assert len(data["hits"]) == 2


def test_format_csv_contains_header(report_with_hits):
    out = format_csv(report_with_hits)
    assert out.startswith("key,severity,reason")


def test_format_csv_contains_rows(report_with_hits):
    out = format_csv(report_with_hits)
    assert "API_KEY" in out
    assert "DB_PASS" in out
