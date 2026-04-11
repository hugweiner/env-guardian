"""Tests for env_guardian.squasher."""
import pytest

from env_guardian.squasher import squash_env, SquashReport


@pytest.fixture()
def unique_env():
    return {"APP_NAME": "myapp", "APP_PORT": "8080", "APP_ENV": "production"}


@pytest.fixture()
def dup_env():
    return {
        "ALPHA": "same",
        "BETA": "same",
        "GAMMA": "different",
        "DELTA": "same",
    }


def test_squash_returns_report(unique_env):
    report = squash_env(unique_env)
    assert isinstance(report, SquashReport)


def test_clean_env_produces_no_duplicates(unique_env):
    report = squash_env(unique_env)
    assert report.is_clean()


def test_clean_env_duplicate_count_is_zero(unique_env):
    report = squash_env(unique_env)
    assert report.duplicate_count() == 0


def test_clean_env_summary(unique_env):
    report = squash_env(unique_env)
    assert "No duplicate" in report.summary()


def test_duplicate_values_detected(dup_env):
    report = squash_env(dup_env)
    assert not report.is_clean()


def test_duplicate_count_correct(dup_env):
    # ALPHA, BETA, DELTA share "same" -> 2 duplicates removed
    report = squash_env(dup_env)
    assert report.duplicate_count() == 2


def test_first_strategy_keeps_alphabetical_first(dup_env):
    report = squash_env(dup_env, strategy="first")
    canonical_keys = {g.canonical_key for g in report.groups if g.value == "same"}
    assert "ALPHA" in canonical_keys


def test_last_strategy_keeps_alphabetical_last(dup_env):
    report = squash_env(dup_env, strategy="last")
    canonical_keys = {g.canonical_key for g in report.groups if g.value == "same"}
    assert "DELTA" in canonical_keys


def test_squashed_env_excludes_duplicate_keys(dup_env):
    report = squash_env(dup_env, strategy="first")
    assert "BETA" not in report.squashed_env
    assert "DELTA" not in report.squashed_env


def test_squashed_env_retains_canonical_key(dup_env):
    report = squash_env(dup_env, strategy="first")
    assert "ALPHA" in report.squashed_env
    assert report.squashed_env["ALPHA"] == "same"


def test_unique_values_preserved(dup_env):
    report = squash_env(dup_env)
    assert "GAMMA" in report.squashed_env
    assert report.squashed_env["GAMMA"] == "different"


def test_summary_mentions_squashed_count(dup_env):
    report = squash_env(dup_env)
    assert "2" in report.summary()


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        squash_env({"A": "1"}, strategy="random")


def test_empty_env_is_clean():
    report = squash_env({})
    assert report.is_clean()
    assert report.squashed_env == {}
