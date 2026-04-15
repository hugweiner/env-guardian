"""Tests for env_guardian.limiter."""
import pytest
from env_guardian.limiter import limit_env, LimitReport


@pytest.fixture
def mixed_env():
    return {
        "SHORT": "hi",
        "MEDIUM": "hello",
        "LONG": "this_is_a_very_long_value_string",
        "EMPTY": "",
    }


def test_no_constraints_produces_no_violations(mixed_env):
    report = limit_env(mixed_env)
    assert report.is_clean()
    assert report.violation_count() == 0


def test_min_length_flags_short_value(mixed_env):
    report = limit_env(mixed_env, min_length=5)
    keys = [v.key for v in report.violations]
    assert "SHORT" in keys
    assert "EMPTY" in keys


def test_max_length_flags_long_value(mixed_env):
    report = limit_env(mixed_env, max_length=10)
    keys = [v.key for v in report.violations]
    assert "LONG" in keys


def test_max_length_does_not_flag_short_value(mixed_env):
    report = limit_env(mixed_env, max_length=10)
    keys = [v.key for v in report.violations]
    assert "SHORT" not in keys


def test_violation_kind_too_short(mixed_env):
    report = limit_env(mixed_env, min_length=5)
    short_violations = [v for v in report.violations if v.key == "SHORT"]
    assert short_violations[0].kind == "too_short"


def test_violation_kind_too_long(mixed_env):
    report = limit_env(mixed_env, max_length=5)
    long_violations = [v for v in report.violations if v.key == "LONG"]
    assert long_violations[0].kind == "too_long"


def test_violation_actual_length_correct():
    env = {"KEY": "abc"}
    report = limit_env(env, min_length=10)
    assert report.violations[0].actual_length == 3


def test_per_key_override_min():
    env = {"A": "hi", "B": "hi"}
    report = limit_env(env, min_length=10, per_key={"A": {"min": 1}})
    keys = [v.key for v in report.violations]
    assert "A" not in keys
    assert "B" in keys


def test_per_key_override_max():
    env = {"A": "hello_world", "B": "hello_world"}
    report = limit_env(env, max_length=5, per_key={"A": {"max": 100}})
    keys = [v.key for v in report.violations]
    assert "A" not in keys
    assert "B" in keys


def test_summary_clean():
    report = limit_env({"KEY": "value"})
    assert "within" in report.summary()


def test_summary_dirty():
    report = limit_env({"KEY": "v"}, min_length=5)
    assert "violation" in report.summary()


def test_report_env_preserved():
    env = {"X": "abc"}
    report = limit_env(env)
    assert report.env == env


def test_str_too_short():
    from env_guardian.limiter import LimitViolation
    v = LimitViolation(key="K", value="a", min_length=5, max_length=None, actual_length=1, kind="too_short")
    assert "too short" in str(v)


def test_str_too_long():
    from env_guardian.limiter import LimitViolation
    v = LimitViolation(key="K", value="aaaaaaa", min_length=None, max_length=3, actual_length=7, kind="too_long")
    assert "too long" in str(v)
