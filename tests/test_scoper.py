"""Tests for env_guardian.scoper."""
import pytest
from env_guardian.scoper import scope_env, ScopeReport


@pytest.fixture()
def mixed_env():
    return {
        "PROD_DATABASE_URL": "postgres://prod/db",
        "PROD_SECRET_KEY": "prod-secret",
        "DEV_DATABASE_URL": "postgres://dev/db",
        "DEV_DEBUG": "true",
        "STAGING_API_URL": "https://staging.example.com",
        "SHARED_KEY": "shared-value",
        "LOG_LEVEL": "info",
    }


def test_scope_returns_report(mixed_env):
    report = scope_env(mixed_env, ["PROD", "DEV", "STAGING"])
    assert isinstance(report, ScopeReport)


def test_prod_keys_assigned_to_prod_scope(mixed_env):
    report = scope_env(mixed_env, ["PROD", "DEV", "STAGING"])
    scopes = [e.scope for e in report.entries]
    assert scopes.count("PROD") == 2


def test_dev_keys_assigned_to_dev_scope(mixed_env):
    report = scope_env(mixed_env, ["PROD", "DEV", "STAGING"])
    dev_entries = report.by_scope("DEV")
    assert len(dev_entries) == 2


def test_strip_prefix_removes_scope_prefix(mixed_env):
    report = scope_env(mixed_env, ["PROD"], strip_prefix=True)
    keys = [e.key for e in report.by_scope("PROD")]
    assert "DATABASE_URL" in keys
    assert "SECRET_KEY" in keys


def test_no_strip_prefix_keeps_original_key(mixed_env):
    report = scope_env(mixed_env, ["PROD"], strip_prefix=False)
    keys = [e.key for e in report.by_scope("PROD")]
    assert "PROD_DATABASE_URL" in keys


def test_original_key_preserved(mixed_env):
    report = scope_env(mixed_env, ["PROD"])
    entry = next(e for e in report.entries if e.key == "DATABASE_URL" and e.scope == "PROD")
    assert entry.original_key == "PROD_DATABASE_URL"


def test_unscoped_keys_collected(mixed_env):
    report = scope_env(mixed_env, ["PROD", "DEV", "STAGING"])
    assert "SHARED_KEY" in report.unscoped
    assert "LOG_LEVEL" in report.unscoped


def test_unscoped_count_correct(mixed_env):
    report = scope_env(mixed_env, ["PROD", "DEV", "STAGING"])
    assert len(report.unscoped) == 2


def test_scope_names_returns_unique_scopes(mixed_env):
    report = scope_env(mixed_env, ["PROD", "DEV", "STAGING"])
    names = report.scope_names()
    assert set(names) == {"PROD", "DEV", "STAGING"}


def test_scoped_env_returns_flat_dict(mixed_env):
    report = scope_env(mixed_env, ["PROD"])
    env = report.scoped_env("PROD")
    assert env == {"DATABASE_URL": "postgres://prod/db", "SECRET_KEY": "prod-secret"}


def test_case_insensitive_matching():
    env = {"prod_api_key": "secret", "OTHER": "val"}
    report = scope_env(env, ["PROD"], separator="_", case_sensitive=False)
    assert len(report.by_scope("PROD")) == 1


def test_custom_separator():
    env = {"PROD.API_KEY": "s3cr3t", "DEV.API_KEY": "dev-key"}
    report = scope_env(env, ["PROD", "DEV"], separator=".", case_sensitive=True)
    assert len(report.by_scope("PROD")) == 1
    assert report.by_scope("PROD")[0].key == "API_KEY"


def test_summary_contains_scope_count(mixed_env):
    report = scope_env(mixed_env, ["PROD", "DEV", "STAGING"])
    assert "3 scope" in report.summary()


def test_summary_contains_unscoped_count(mixed_env):
    report = scope_env(mixed_env, ["PROD", "DEV", "STAGING"])
    assert "2 unscoped" in report.summary()


def test_empty_env_produces_empty_report():
    report = scope_env({}, ["PROD", "DEV"])
    assert report.entries == []
    assert report.unscoped == {}
