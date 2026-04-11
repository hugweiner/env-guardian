"""Tests for env_guardian.flattener."""
import pytest
from env_guardian.flattener import flatten_env, FlattenReport


@pytest.fixture
def simple_env():
    return {
        "APP__DB__HOST": "localhost",
        "APP__DB__PORT": "5432",
        "DEBUG": "true",
    }


def test_flatten_returns_report(simple_env):
    report = flatten_env(simple_env)
    assert isinstance(report, FlattenReport)


def test_clean_env_produces_no_warnings():
    env = {"APP": "value", "DEBUG": "true"}
    report = flatten_env(env)
    assert report.is_clean()
    assert report.summary() == "No keys were flattened."


def test_double_underscore_key_is_flattened(simple_env):
    report = flatten_env(simple_env)
    assert "APP_DB_HOST" in report.env
    assert "APP_DB_PORT" in report.env


def test_non_separator_key_preserved(simple_env):
    report = flatten_env(simple_env)
    assert "DEBUG" in report.env
    assert report.env["DEBUG"] == "true"


def test_original_key_removed_after_flatten(simple_env):
    report = flatten_env(simple_env)
    assert "APP__DB__HOST" not in report.env


def test_value_preserved_after_flatten(simple_env):
    report = flatten_env(simple_env)
    assert report.env["APP_DB_HOST"] == "localhost"
    assert report.env["APP_DB_PORT"] == "5432"


def test_warnings_generated_for_flattened_keys(simple_env):
    report = flatten_env(simple_env)
    flattened_originals = {w.original for w in report.warnings}
    assert "APP__DB__HOST" in flattened_originals
    assert "APP__DB__PORT" in flattened_originals


def test_summary_reports_count(simple_env):
    report = flatten_env(simple_env)
    assert "2 key(s) flattened" in report.summary()


def test_custom_separator():
    env = {"APP..HOST": "localhost", "PORT": "80"}
    report = flatten_env(env, separator="..", replacement="_")
    assert "APP_HOST" in report.env
    assert "PORT" in report.env


def test_custom_replacement():
    env = {"APP__HOST": "localhost"}
    report = flatten_env(env, separator="__", replacement=".")
    assert "APP.HOST" in report.env


def test_collision_last_wins():
    env = {"A__B": "first", "A_B": "direct"}
    # After flattening A__B -> A_B; A_B already present — last-wins means A__B overwrites
    env_ordered = {"A_B": "direct", "A__B": "overwriter"}
    report = flatten_env(env_ordered, collision="last")
    assert report.env["A_B"] == "overwriter"


def test_collision_first_wins():
    env_ordered = {"A_B": "direct", "A__B": "overwriter"}
    report = flatten_env(env_ordered, collision="first")
    assert report.env["A_B"] == "direct"


def test_collision_first_wins_skip_warning_present():
    env_ordered = {"A_B": "direct", "A__B": "overwriter"}
    report = flatten_env(env_ordered, collision="first")
    skip_warnings = [w for w in report.warnings if "skipped" in w.reason]
    assert len(skip_warnings) == 1


def test_empty_separator_raises():
    with pytest.raises(ValueError, match="separator must not be empty"):
        flatten_env({"KEY": "val"}, separator="")


def test_warning_str_representation():
    env = {"APP__HOST": "localhost"}
    report = flatten_env(env)
    assert len(report.warnings) == 1
    text = str(report.warnings[0])
    assert "[FLATTEN]" in text
    assert "APP__HOST" in text
