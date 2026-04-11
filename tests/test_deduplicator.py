"""Tests for env_guardian.deduplicator."""
import pytest

from env_guardian.deduplicator import DeduplicateReport, DuplicateGroup, deduplicate_env


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def unique_env():
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


@pytest.fixture()
def dup_env():
    return {
        "DB_PASS": "secret123",
        "API_SECRET": "secret123",
        "HOST": "localhost",
        "REPLICA_HOST": "localhost",
        "PORT": "8080",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_clean_env_produces_no_groups(unique_env):
    report = deduplicate_env(unique_env)
    assert report.is_clean()


def test_clean_env_summary(unique_env):
    report = deduplicate_env(unique_env)
    assert "No duplicate" in report.summary()


def test_duplicate_groups_detected(dup_env):
    report = deduplicate_env(dup_env)
    assert not report.is_clean()
    assert len(report.groups) == 2


def test_duplicate_group_keys_sorted(dup_env):
    report = deduplicate_env(dup_env)
    secret_group = next(g for g in report.groups if g.value == "secret123")
    assert secret_group.keys == ["API_SECRET", "DB_PASS"]


def test_duplicate_count(dup_env):
    report = deduplicate_env(dup_env)
    # 2 keys share "secret123", 2 keys share "localhost" => 4 total
    assert report.duplicate_count() == 4


def test_summary_mentions_group_count(dup_env):
    report = deduplicate_env(dup_env)
    assert "2 duplicate group(s)" in report.summary()


def test_keep_first_drops_later_keys(dup_env):
    report = deduplicate_env(dup_env, keep="first")
    # For "secret123": sorted keys are [API_SECRET, DB_PASS] -> keep API_SECRET
    assert "API_SECRET" in report.deduplicated_env
    assert "DB_PASS" not in report.deduplicated_env


def test_keep_last_drops_earlier_keys(dup_env):
    report = deduplicate_env(dup_env, keep="last")
    # For "secret123": sorted keys are [API_SECRET, DB_PASS] -> keep DB_PASS
    assert "DB_PASS" in report.deduplicated_env
    assert "API_SECRET" not in report.deduplicated_env


def test_unique_keys_always_preserved(dup_env):
    report = deduplicate_env(dup_env)
    assert "PORT" in report.deduplicated_env


def test_empty_values_ignored_by_default():
    env = {"A": "", "B": "", "C": "real"}
    report = deduplicate_env(env, ignore_empty=True)
    assert report.is_clean()


def test_empty_values_included_when_flag_off():
    env = {"A": "", "B": "", "C": "real"}
    report = deduplicate_env(env, ignore_empty=False)
    assert not report.is_clean()
    assert len(report.groups) == 1


def test_duplicate_group_str():
    group = DuplicateGroup(value="x", keys=["A", "B"])
    assert "x" in str(group)
    assert "A" in str(group)
