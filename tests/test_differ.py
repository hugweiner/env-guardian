"""Tests for differ.py and diff_formatter.py."""

import json
import pytest

from env_guardian.differ import build_diff_report, DiffLine
from env_guardian.diff_formatter import format_text, format_json, format_csv


SOURCE = {"APP_NAME": "myapp", "DB_HOST": "localhost", "SECRET": "old_secret"}
TARGET = {"APP_NAME": "myapp", "DB_HOST": "prod.db", "NEW_KEY": "hello"}


@pytest.fixture
def report():
    return build_diff_report(SOURCE, TARGET)


def test_unchanged_key_detected(report):
    keys = {l.key: l.status for l in report.lines}
    assert keys["APP_NAME"] == "unchanged"


def test_changed_key_detected(report):
    keys = {l.key: l.status for l in report.lines}
    assert keys["DB_HOST"] == "changed"


def test_removed_key_detected(report):
    keys = {l.key: l.status for l in report.lines}
    assert keys["SECRET"] == "removed"


def test_added_key_detected(report):
    keys = {l.key: l.status for l in report.lines}
    assert keys["NEW_KEY"] == "added"


def test_is_clean_false_when_differences(report):
    assert not report.is_clean()


def test_is_clean_true_when_identical():
    r = build_diff_report({"A": "1"}, {"A": "1"})
    assert r.is_clean()


def test_summary_counts(report):
    summary = report.summary()
    assert "+1 added" in summary
    assert "-1 removed" in summary
    assert "~1 changed" in summary


def test_diff_line_str_added():
    line = DiffLine("NEW_KEY", "added", target_value="hello")
    assert str(line).startswith("+")
    assert "NEW_KEY" in str(line)


def test_diff_line_str_removed():
    line = DiffLine("OLD_KEY", "removed", source_value="bye")
    assert str(line).startswith("-")


def test_diff_line_str_changed():
    line = DiffLine("KEY", "changed", source_value="a", target_value="b")
    assert str(line).startswith("~")
    assert "->" in str(line)


def test_format_text_clean():
    r = build_diff_report({"A": "1"}, {"A": "1"})
    text = format_text(r)
    assert "No differences found" in text


def test_format_text_with_diff(report):
    text = format_text(report)
    assert "NEW_KEY" in text
    assert "SECRET" in text


def test_format_json_valid(report):
    raw = format_json(report)
    data = json.loads(raw)
    assert "diff" in data
    assert "summary" in data
    keys = [entry["key"] for entry in data["diff"]]
    assert "NEW_KEY" in keys


def test_format_csv_has_header(report):
    csv_output = format_csv(report)
    assert "key,status,source_value,target_value" in csv_output


def test_format_csv_has_rows(report):
    csv_output = format_csv(report)
    assert "NEW_KEY" in csv_output
    assert "SECRET" in csv_output
