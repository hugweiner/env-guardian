"""Tests for env_guardian.classifier."""

import pytest
from env_guardian.classifier import classify_env, ClassifyEntry, ClassifyReport


@pytest.fixture
def mixed_env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "API_SECRET": "s3cr3t",
        "LOG_LEVEL": "INFO",
        "APP_PORT": "8080",
        "FEATURE_FLAG_DARK_MODE": "true",
        "MAX_RETRIES": "3",
        "ENVIRONMENT": "production",
        "PLAIN_KEY": "value",
    }


def test_classify_returns_report(mixed_env):
    report = classify_env(mixed_env)
    assert isinstance(report, ClassifyReport)
    assert len(report.entries) == len(mixed_env)


def test_each_entry_has_group(mixed_env):
    report = classify_env(mixed_env)
    for entry in report.entries:
        assert isinstance(entry, ClassifyEntry)
        assert entry.group


def test_database_url_classified_as_database(mixed_env):
    report = classify_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "DATABASE_URL")
    assert entry.group == "database"


def test_secret_key_classified_as_secret(mixed_env):
    report = classify_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "API_SECRET")
    assert entry.group == "secret"


def test_log_level_classified_as_logging(mixed_env):
    report = classify_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "LOG_LEVEL")
    assert entry.group == "logging"


def test_port_key_classified_as_network(mixed_env):
    report = classify_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "APP_PORT")
    assert entry.group == "network"


def test_feature_flag_classified_correctly(mixed_env):
    report = classify_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "FEATURE_FLAG_DARK_MODE")
    assert entry.group == "feature_flag"


def test_unknown_key_falls_back_to_general():
    report = classify_env({"PLAIN_KEY": "value"})
    assert report.entries[0].group == "general"


def test_by_group_returns_dict(mixed_env):
    report = classify_env(mixed_env)
    groups = report.by_group()
    assert isinstance(groups, dict)
    assert "secret" in groups
    assert "database" in groups


def test_count_by_group(mixed_env):
    report = classify_env(mixed_env)
    counts = report.count_by_group()
    assert counts["secret"] == 1
    assert counts["database"] == 1


def test_summary_contains_group_names(mixed_env):
    report = classify_env(mixed_env)
    s = report.summary()
    assert "secret" in s
    assert "general" in s


def test_empty_env_produces_no_entries():
    report = classify_env({})
    assert report.entries == []
    assert report.summary() == "no entries"


def test_classify_entry_str():
    entry = ClassifyEntry(key="DB_HOST", value="localhost", group="database")
    assert "database" in str(entry)
    assert "DB_HOST" in str(entry)
