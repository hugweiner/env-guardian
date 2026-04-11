"""Tests for env_guardian.rotator."""
from __future__ import annotations

import pytest

from env_guardian.rotator import RotateReport, rotate_env


@pytest.fixture()
def clean_env() -> dict:
    return {"DATABASE_URL": "postgres://localhost/db", "API_KEY": "secret123"}


@pytest.fixture()
def stale_env() -> dict:
    return {
        "DATABASE_URL_OLD": "postgres://localhost/old",
        "TOKEN_BACKUP": "abc",
        "CURRENT_KEY": "xyz",
    }


def test_rotate_returns_report(clean_env):
    report = rotate_env(clean_env)
    assert isinstance(report, RotateReport)


def test_all_keys_processed(clean_env):
    report = rotate_env(clean_env)
    assert len(report.entries) == len(clean_env)


def test_clean_env_has_no_stale(clean_env):
    report = rotate_env(clean_env)
    assert report.is_clean()
    assert report.stale_count == 0


def test_stale_suffix_old_detected(stale_env):
    report = rotate_env(stale_env)
    stale_keys = {e.key for e in report.entries if e.stale}
    assert "DATABASE_URL_OLD" in stale_keys


def test_stale_suffix_backup_detected(stale_env):
    report = rotate_env(stale_env)
    stale_keys = {e.key for e in report.entries if e.stale}
    assert "TOKEN_BACKUP" in stale_keys


def test_non_stale_key_not_flagged(stale_env):
    report = rotate_env(stale_env)
    current = next(e for e in report.entries if e.key == "CURRENT_KEY")
    assert not current.stale


def test_stale_count_correct(stale_env):
    report = rotate_env(stale_env)
    assert report.stale_count == 2


def test_rotated_key_uses_custom_suffix(clean_env):
    report = rotate_env(clean_env, suffix="2099")
    for entry in report.entries:
        assert entry.rotated_key.endswith("_ROTATED_2099")


def test_rotated_key_uses_year_by_default(clean_env):
    from datetime import date
    year = str(date.today().year)
    report = rotate_env(clean_env)
    for entry in report.entries:
        assert year in entry.rotated_key


def test_rotated_env_contains_rotated_keys(clean_env):
    report = rotate_env(clean_env)
    rotated = report.rotated_env
    for entry in report.entries:
        assert entry.rotated_key in rotated


def test_rotated_env_preserves_values(clean_env):
    report = rotate_env(clean_env)
    rotated = report.rotated_env
    for entry in report.entries:
        assert rotated[entry.rotated_key] == entry.value


def test_flag_stale_false_skips_detection(stale_env):
    report = rotate_env(stale_env, flag_stale=False)
    assert report.stale_count == 0


def test_summary_contains_counts(stale_env):
    report = rotate_env(stale_env)
    summary = report.summary()
    assert "3" in summary
    assert "2" in summary
