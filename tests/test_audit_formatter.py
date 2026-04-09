"""Tests for env_guardian.audit_formatter module."""

import json
import csv
import io
import pytest

from env_guardian.auditor import AuditReport
from env_guardian.audit_formatter import format_text, format_json, format_csv


@pytest.fixture
def clean_report():
    return AuditReport()


@pytest.fixture
def report_with_issues():
    r = AuditReport()
    r.add_issue("TOKEN", "high", "Empty secret value.")
    r.add_issue("MY KEY", "medium", "Key contains spaces.")
    r.add_issue("lower_key", "low", "Key is not uppercase.")
    return r


def test_format_text_clean(clean_report):
    text = format_text(clean_report)
    assert "passed" in text.lower()


def test_format_text_with_issues(report_with_issues):
    text = format_text(report_with_issues)
    assert "[HIGH]" in text
    assert "[MEDIUM]" in text
    assert "[LOW]" in text
    assert "TOKEN" in text


def test_format_text_severity_order(report_with_issues):
    text = format_text(report_with_issues)
    high_pos = text.index("[HIGH]")
    medium_pos = text.index("[MEDIUM]")
    low_pos = text.index("[LOW]")
    assert high_pos < medium_pos < low_pos


def test_format_json_clean(clean_report):
    data = json.loads(format_json(clean_report))
    assert data["clean"] is True
    assert data["issues"] == []


def test_format_json_with_issues(report_with_issues):
    data = json.loads(format_json(report_with_issues))
    assert data["clean"] is False
    assert len(data["issues"]) == 3
    severities = [i["severity"] for i in data["issues"]]
    assert severities[0] == "high"


def test_format_json_issue_fields(report_with_issues):
    data = json.loads(format_json(report_with_issues))
    issue = data["issues"][0]
    assert "key" in issue
    assert "severity" in issue
    assert "message" in issue


def test_format_csv_clean(clean_report):
    csv_text = format_csv(clean_report)
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)
    assert rows == []


def test_format_csv_with_issues(report_with_issues):
    csv_text = format_csv(report_with_issues)
    reader = csv.DictReader(io.StringIO(csv_text))
    rows = list(reader)
    assert len(rows) == 3
    assert rows[0]["severity"] == "high"


def test_format_csv_headers(report_with_issues):
    csv_text = format_csv(report_with_issues)
    first_line = csv_text.splitlines()[0]
    assert "key" in first_line
    assert "severity" in first_line
    assert "message" in first_line
