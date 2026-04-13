"""Tests for env_guardian.injector and env_guardian.inject_formatter."""
import json

import pytest

from env_guardian.injector import inject_env
from env_guardian.inject_formatter import format_csv, format_json, format_text


@pytest.fixture()
def base_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "APP_ENV": "production"}


def test_inject_returns_report(base_env):
    report = inject_env(base_env, {"NEW_KEY": "value"})
    assert report is not None


def test_new_key_injected(base_env):
    report = inject_env(base_env, {"NEW_KEY": "hello"})
    assert report.result_env["NEW_KEY"] == "hello"


def test_injected_count_correct(base_env):
    report = inject_env(base_env, {"X": "1", "Y": "2"})
    assert report.injected_count == 2


def test_overwrite_existing_key_by_default(base_env):
    report = inject_env(base_env, {"DB_HOST": "remotehost"})
    assert report.result_env["DB_HOST"] == "remotehost"


def test_overwritten_count_correct(base_env):
    report = inject_env(base_env, {"DB_HOST": "remotehost", "DB_PORT": "3306"})
    assert report.overwritten_count == 2


def test_no_overwrite_skips_existing_key(base_env):
    report = inject_env(base_env, {"DB_HOST": "remotehost"}, overwrite=False)
    assert report.result_env["DB_HOST"] == "localhost"


def test_no_overwrite_still_injects_new_key(base_env):
    report = inject_env(base_env, {"NEW_KEY": "val"}, overwrite=False)
    assert report.result_env["NEW_KEY"] == "val"


def test_previous_value_stored_on_overwrite(base_env):
    report = inject_env(base_env, {"DB_HOST": "newhost"})
    entry = next(e for e in report.entries if e.key == "DB_HOST")
    assert entry.previous_value == "localhost"


def test_is_clean_when_no_overwrites(base_env):
    report = inject_env(base_env, {"BRAND_NEW": "yes"})
    assert report.is_clean()


def test_is_not_clean_when_overwrites_present(base_env):
    report = inject_env(base_env, {"DB_HOST": "other"})
    assert not report.is_clean()


def test_base_env_unchanged(base_env):
    original = dict(base_env)
    inject_env(base_env, {"DB_HOST": "other"})
    assert base_env == original


def test_format_text_contains_header(base_env):
    report = inject_env(base_env, {"FOO": "bar"})
    text = format_text(report)
    assert "Inject Report" in text


def test_format_text_shows_new_tag(base_env):
    report = inject_env(base_env, {"FOO": "bar"})
    text = format_text(report)
    assert "[new]" in text


def test_format_text_shows_overwrite_tag(base_env):
    report = inject_env(base_env, {"DB_HOST": "other"})
    text = format_text(report)
    assert "[overwrite]" in text


def test_format_json_valid(base_env):
    report = inject_env(base_env, {"FOO": "bar", "DB_HOST": "x"})
    data = json.loads(format_json(report))
    assert "entries" in data
    assert data["summary"]["injected"] == 1
    assert data["summary"]["overwritten"] == 1


def test_format_csv_contains_header(base_env):
    report = inject_env(base_env, {"FOO": "bar"})
    csv_text = format_csv(report)
    assert "key" in csv_text
    assert "overwritten" in csv_text


def test_format_csv_contains_key(base_env):
    report = inject_env(base_env, {"FOO": "bar"})
    csv_text = format_csv(report)
    assert "FOO" in csv_text
