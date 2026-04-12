"""Tests for env_guardian.prefixer."""
import pytest
from env_guardian.prefixer import add_prefix, strip_prefix, PrefixReport


@pytest.fixture()
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "guardian",
        "SECRET_KEY": "s3cr3t",
    }


# --- add_prefix ---

def test_add_prefix_returns_report(base_env):
    report = add_prefix(base_env, "MYAPP_")
    assert isinstance(report, PrefixReport)


def test_add_prefix_all_keys_prefixed(base_env):
    report = add_prefix(base_env, "MYAPP_")
    for entry in report.entries:
        assert entry.new_key.startswith("MYAPP_")


def test_add_prefix_values_preserved(base_env):
    report = add_prefix(base_env, "MYAPP_")
    result = report.result_env
    assert result["MYAPP_DB_HOST"] == "localhost"
    assert result["MYAPP_SECRET_KEY"] == "s3cr3t"


def test_add_prefix_modified_count(base_env):
    report = add_prefix(base_env, "MYAPP_")
    assert report.modified_count == len(base_env)


def test_add_prefix_skip_already_prefixed():
    env = {"MYAPP_DB": "x", "OTHER": "y"}
    report = add_prefix(env, "MYAPP_", skip_already_prefixed=True)
    result = report.result_env
    assert "MYAPP_DB" in result
    assert "MYAPP_MYAPP_DB" not in result
    assert result["MYAPP_OTHER"] == "y"


def test_add_prefix_no_skip_re_prefixes_existing():
    env = {"MYAPP_DB": "x"}
    report = add_prefix(env, "MYAPP_", skip_already_prefixed=False)
    result = report.result_env
    assert "MYAPP_MYAPP_DB" in result


def test_add_prefix_summary_contains_modified(base_env):
    report = add_prefix(base_env, "X_")
    assert str(len(base_env)) in report.summary()


# --- strip_prefix ---

def test_strip_prefix_returns_report(base_env):
    report = strip_prefix(base_env, "DB_")
    assert isinstance(report, PrefixReport)


def test_strip_prefix_removes_matching_prefix(base_env):
    report = strip_prefix(base_env, "DB_")
    result = report.result_env
    assert "HOST" in result
    assert "PORT" in result


def test_strip_prefix_non_matching_kept_by_default(base_env):
    report = strip_prefix(base_env, "DB_", keep_non_matching=True)
    result = report.result_env
    assert "APP_NAME" in result
    assert "SECRET_KEY" in result


def test_strip_prefix_non_matching_excluded_when_flag_false(base_env):
    report = strip_prefix(base_env, "DB_", keep_non_matching=False)
    result = report.result_env
    assert "APP_NAME" not in result
    assert "HOST" in result


def test_strip_prefix_action_labels(base_env):
    report = strip_prefix(base_env, "DB_")
    actions = {e.original_key: e.action for e in report.entries}
    assert actions["DB_HOST"] == "stripped"
    assert actions["APP_NAME"] == "unchanged"


def test_strip_prefix_values_preserved(base_env):
    report = strip_prefix(base_env, "DB_")
    result = report.result_env
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"


def test_prefix_entry_str_format(base_env):
    report = add_prefix({"KEY": "val"}, "PRE_")
    entry = report.entries[0]
    assert "KEY" in str(entry)
    assert "PRE_KEY" in str(entry)
    assert "added" in str(entry)
