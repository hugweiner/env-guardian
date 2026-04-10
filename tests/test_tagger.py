"""Tests for env_guardian.tagger."""

import pytest

from env_guardian.tagger import TagEntry, TagReport, tag_env


@pytest.fixture
def mixed_env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "supersecret",
        "API_TOKEN": "abc123",
        "ENABLE_FEATURE_X": "true",
        "APP_PORT": "8080",
        "APP_NAME": "myapp",
    }


def test_tag_env_returns_report(mixed_env):
    report = tag_env(mixed_env)
    assert isinstance(report, TagReport)
    assert len(report.entries) == len(mixed_env)


def test_each_entry_has_key_and_value(mixed_env):
    report = tag_env(mixed_env)
    keys = {e.key for e in report.entries}
    assert keys == set(mixed_env.keys())


def test_database_url_tagged_as_database_and_url(mixed_env):
    report = tag_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "DATABASE_URL")
    assert "database" in entry.tags
    assert "url" in entry.tags


def test_secret_key_tagged_as_secret(mixed_env):
    report = tag_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "SECRET_KEY")
    assert "secret" in entry.tags


def test_api_token_tagged_as_secret(mixed_env):
    report = tag_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "API_TOKEN")
    assert "secret" in entry.tags


def test_feature_flag_tagged_correctly(mixed_env):
    report = tag_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "ENABLE_FEATURE_X")
    assert "feature_flag" in entry.tags


def test_app_port_tagged_as_infra(mixed_env):
    report = tag_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "APP_PORT")
    assert "infra" in entry.tags


def test_unrecognised_key_has_no_tags(mixed_env):
    report = tag_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "APP_NAME")
    assert entry.tags == []


def test_by_tag_filters_correctly(mixed_env):
    report = tag_env(mixed_env)
    secrets = report.by_tag("secret")
    keys = {e.key for e in secrets}
    assert "SECRET_KEY" in keys
    assert "API_TOKEN" in keys
    assert "APP_NAME" not in keys


def test_tag_names_returns_sorted_unique(mixed_env):
    report = tag_env(mixed_env)
    names = report.tag_names()
    assert names == sorted(set(names))
    assert "secret" in names
    assert "database" in names


def test_untagged_returns_only_untagged(mixed_env):
    report = tag_env(mixed_env)
    untagged = report.untagged()
    assert all(e.tags == [] for e in untagged)
    assert any(e.key == "APP_NAME" for e in untagged)


def test_extra_rules_applied(mixed_env):
    report = tag_env(mixed_env, extra_rules={"app": ["APP_"]})
    entry = next(e for e in report.entries if e.key == "APP_NAME")
    assert "app" in entry.tags


def test_manual_tags_applied(mixed_env):
    report = tag_env(mixed_env, manual_tags={"APP_NAME": ["custom"]})
    entry = next(e for e in report.entries if e.key == "APP_NAME")
    assert "custom" in entry.tags


def test_summary_string(mixed_env):
    report = tag_env(mixed_env)
    s = report.summary()
    assert str(len(mixed_env)) in s


def test_tag_entry_str():
    entry = TagEntry(key="MY_KEY", value="val", tags=["secret"])
    result = str(entry)
    assert "MY_KEY" in result
    assert "secret" in result
