"""Tests for env_guardian.annotator and env_guardian.annotation_formatter."""
import json

import pytest

from env_guardian.annotator import annotate_env, AnnotationEntry
from env_guardian.annotation_formatter import format_text, format_json, format_csv


@pytest.fixture
def simple_env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "supersecret",
        "CUSTOM_VAR": "hello",
    }


def test_annotate_returns_report(simple_env):
    report = annotate_env(simple_env)
    assert len(report.entries) == 3


def test_builtin_annotation_applied(simple_env):
    report = annotate_env(simple_env)
    by_key = report.by_key()
    assert by_key["DATABASE_URL"].annotation is not None
    assert "database" in by_key["DATABASE_URL"].annotation.lower()


def test_custom_annotation_overrides_builtin(simple_env):
    report = annotate_env(simple_env, annotations={"DATABASE_URL": "My custom note"})
    by_key = report.by_key()
    assert by_key["DATABASE_URL"].annotation == "My custom note"


def test_unknown_key_has_no_annotation(simple_env):
    report = annotate_env(simple_env)
    by_key = report.by_key()
    assert by_key["CUSTOM_VAR"].annotation is None


def test_annotated_count(simple_env):
    report = annotate_env(simple_env)
    # DATABASE_URL and SECRET_KEY have built-in annotations; CUSTOM_VAR does not
    assert report.annotated_count() == 2


def test_unannotated_count(simple_env):
    report = annotate_env(simple_env)
    assert report.unannotated_count() == 1


def test_summary_string(simple_env):
    report = annotate_env(simple_env)
    assert report.summary() == "2/3 keys annotated"


def test_use_builtins_false_leaves_known_keys_unannotated():
    env = {"SECRET_KEY": "abc"}
    report = annotate_env(env, use_builtins=False)
    assert report.entries[0].annotation is None


def test_custom_annotation_without_builtins():
    env = {"MY_KEY": "value"}
    report = annotate_env(env, annotations={"MY_KEY": "Custom"}, use_builtins=False)
    assert report.by_key()["MY_KEY"].annotation == "Custom"


def test_annotation_entry_str_with_annotation():
    entry = AnnotationEntry(key="FOO", value="bar", annotation="A note")
    assert str(entry) == "FOO=bar # A note"


def test_annotation_entry_str_without_annotation():
    entry = AnnotationEntry(key="FOO", value="bar", annotation=None)
    assert str(entry) == "FOO=bar"


def test_format_text_contains_header(simple_env):
    report = annotate_env(simple_env)
    text = format_text(report)
    assert "Annotation Report" in text


def test_format_text_contains_all_keys(simple_env):
    report = annotate_env(simple_env)
    text = format_text(report)
    for key in simple_env:
        assert key in text


def test_format_json_valid(simple_env):
    report = annotate_env(simple_env)
    data = json.loads(format_json(report))
    assert "entries" in data
    assert "summary" in data
    assert len(data["entries"]) == 3


def test_format_csv_has_header(simple_env):
    report = annotate_env(simple_env)
    csv_output = format_csv(report)
    assert csv_output.splitlines()[0] == "key,value,annotation"


def test_format_csv_row_count(simple_env):
    report = annotate_env(simple_env)
    lines = [l for l in format_csv(report).splitlines() if l]
    # header + 3 data rows
    assert len(lines) == 4
