"""Tests for env_guardian.expander."""
import pytest
from env_guardian.expander import expand_env, ExpandReport


@pytest.fixture()
def mixed_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_ENV": "production",
        "LOG_LEVEL": "INFO",          # already canonical — no expansion
        "MY_CUSTOM_VAR": "hello",    # unknown — no expansion
    }


def test_expand_returns_report(mixed_env):
    report = expand_env(mixed_env)
    assert isinstance(report, ExpandReport)


def test_known_key_is_expanded(mixed_env):
    report = expand_env(mixed_env)
    expanded = report.expanded_env()
    assert "DATABASE_HOST" in expanded
    assert "DB_HOST" not in expanded


def test_expanded_value_preserved(mixed_env):
    report = expand_env(mixed_env)
    assert report.expanded_env()["DATABASE_HOST"] == "localhost"


def test_unknown_key_not_expanded(mixed_env):
    report = expand_env(mixed_env)
    expanded = report.expanded_env()
    assert "MY_CUSTOM_VAR" in expanded


def test_already_canonical_key_not_expanded(mixed_env):
    report = expand_env(mixed_env)
    entry = next(e for e in report.entries if e.key == "LOG_LEVEL")
    assert not entry.was_expanded


def test_expanded_count_correct(mixed_env):
    report = expand_env(mixed_env)
    # DB_HOST, DB_PORT, APP_ENV are in the default map
    assert report.expanded_count() == 3


def test_is_clean_false_when_expansions_exist(mixed_env):
    report = expand_env(mixed_env)
    assert not report.is_clean()


def test_is_clean_true_when_no_expansions():
    env = {"LOG_LEVEL": "DEBUG", "MY_VAR": "val"}
    report = expand_env(env)
    assert report.is_clean()


def test_summary_mentions_expanded_count(mixed_env):
    report = expand_env(mixed_env)
    assert "3" in report.summary()


def test_summary_clean_message():
    env = {"PLAIN_KEY": "value"}
    report = expand_env(env)
    assert "fully expanded" in report.summary()


def test_custom_expansions_override_defaults():
    env = {"SVC_HOST": "api.example.com"}
    custom = {"SVC_HOST": "SERVICE_HOST"}
    report = expand_env(env, expansions=custom)
    assert "SERVICE_HOST" in report.expanded_env()
    assert report.expanded_count() == 1


def test_custom_expansions_do_not_include_defaults():
    env = {"DB_HOST": "localhost"}
    custom = {"SVC_HOST": "SERVICE_HOST"}
    report = expand_env(env, expansions=custom)
    # DB_HOST is NOT in custom map, so it stays as-is
    assert "DB_HOST" in report.expanded_env()
    assert report.expanded_count() == 0


def test_entry_str_expanded():
    env = {"DB_HOST": "localhost"}
    report = expand_env(env)
    entry = report.entries[0]
    text = str(entry)
    assert "DB_HOST" in text
    assert "DATABASE_HOST" in text


def test_entry_str_not_expanded():
    env = {"MY_KEY": "val"}
    report = expand_env(env)
    entry = report.entries[0]
    assert str(entry) == "MY_KEY=val"
