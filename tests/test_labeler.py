"""Tests for env_guardian.labeler."""
import pytest
from env_guardian.labeler import label_env, LabelEntry, LabelReport


@pytest.fixture()
def mixed_env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "SECRET_KEY": "supersecret",
        "REDIS_URL": "redis://localhost:6379",
        "LOG_LEVEL": "INFO",
        "DEBUG": "true",
        "PORT": "8080",
        "AWS_ACCESS_KEY_ID": "AKIA123",
        "UNKNOWN_VAR": "something",
    }


def test_label_env_returns_report(mixed_env):
    report = label_env(mixed_env)
    assert isinstance(report, LabelReport)


def test_all_keys_present_in_report(mixed_env):
    report = label_env(mixed_env)
    keys = {e.key for e in report.entries}
    assert keys == set(mixed_env.keys())


def test_database_url_labeled_as_database(mixed_env):
    report = label_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "DATABASE_URL")
    assert entry.label == "database"
    assert entry.source == "builtin"


def test_secret_key_labeled_as_secret(mixed_env):
    report = label_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "SECRET_KEY")
    assert entry.label == "secret"


def test_redis_url_labeled_as_cache(mixed_env):
    report = label_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "REDIS_URL")
    assert entry.label == "cache"


def test_aws_key_labeled_via_prefix(mixed_env):
    report = label_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "AWS_ACCESS_KEY_ID")
    assert entry.label == "cloud"
    assert entry.source == "prefix"


def test_unknown_key_has_no_label(mixed_env):
    report = label_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "UNKNOWN_VAR")
    assert entry.label is None
    assert entry.source == "none"


def test_custom_label_overrides_builtin(mixed_env):
    report = label_env(mixed_env, custom_labels={"DATABASE_URL": "override-label"})
    entry = next(e for e in report.entries if e.key == "DATABASE_URL")
    assert entry.label == "override-label"
    assert entry.source == "custom"


def test_labeled_count_excludes_none_labels(mixed_env):
    report = label_env(mixed_env)
    labeled = report.labeled_count()
    none_count = sum(1 for e in report.entries if e.label is None)
    assert labeled + none_count == len(mixed_env)


def test_by_label_groups_entries(mixed_env):
    report = label_env(mixed_env)
    groups = report.by_label()
    assert "database" in groups
    assert any(e.key == "DATABASE_URL" for e in groups["database"])


def test_label_names_sorted(mixed_env):
    report = label_env(mixed_env)
    names = report.label_names()
    assert names == sorted(names)


def test_summary_string(mixed_env):
    report = label_env(mixed_env)
    summary = report.summary()
    assert "/" in summary
    assert "labeled" in summary


def test_str_representation():
    entry = LabelEntry(key="FOO", value="bar", label="meta", source="custom")
    result = str(entry)
    assert "FOO" in result
    assert "meta" in result
    assert "custom" in result


def test_empty_env_produces_empty_report():
    report = label_env({})
    assert report.entries == []
    assert report.labeled_count() == 0
