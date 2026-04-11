"""Tests for env_guardian.digester and env_guardian.digest_formatter."""
import hashlib
import json

import pytest

from env_guardian.digester import digest_env, DigestEntry, DigestReport
from env_guardian.digest_formatter import format_text, format_json, format_csv


SIMPLE_ENV = {
    "DATABASE_URL": "postgres://localhost/db",
    "SECRET_KEY": "s3cr3t",
    "DEBUG": "false",
}


# ---------------------------------------------------------------------------
# digester core
# ---------------------------------------------------------------------------

def test_digest_returns_report():
    report = digest_env(SIMPLE_ENV)
    assert isinstance(report, DigestReport)


def test_all_keys_present_in_report():
    report = digest_env(SIMPLE_ENV)
    assert set(report.entries.keys()) == set(SIMPLE_ENV.keys())


def test_checksum_matches_sha256():
    report = digest_env(SIMPLE_ENV)
    expected = hashlib.sha256(b"s3cr3t").hexdigest()
    assert report.checksum_for("SECRET_KEY") == expected


def test_md5_algorithm_used():
    report = digest_env({"KEY": "val"}, algorithm="md5")
    expected = hashlib.md5(b"val").hexdigest()
    assert report.checksum_for("KEY") == expected


def test_sha1_algorithm_used():
    report = digest_env({"KEY": "val"}, algorithm="sha1")
    expected = hashlib.sha1(b"val").hexdigest()
    assert report.checksum_for("KEY") == expected


def test_unsupported_algorithm_raises():
    with pytest.raises(ValueError, match="Unsupported algorithm"):
        digest_env({"K": "v"}, algorithm="blake2b")


def test_fingerprint_is_deterministic():
    r1 = digest_env(SIMPLE_ENV)
    r2 = digest_env(SIMPLE_ENV)
    assert r1.fingerprint() == r2.fingerprint()


def test_fingerprint_changes_when_value_changes():
    env2 = {**SIMPLE_ENV, "DEBUG": "true"}
    r1 = digest_env(SIMPLE_ENV)
    r2 = digest_env(env2)
    assert r1.fingerprint() != r2.fingerprint()


def test_diff_against_clean_when_identical():
    r1 = digest_env(SIMPLE_ENV)
    r2 = digest_env(SIMPLE_ENV)
    assert r1.diff_against(r2) == {}


def test_diff_against_detects_changed_value():
    env2 = {**SIMPLE_ENV, "DEBUG": "true"}
    r1 = digest_env(SIMPLE_ENV)
    r2 = digest_env(env2)
    diff = r1.diff_against(r2)
    assert "DEBUG" in diff


def test_diff_against_detects_added_key():
    env2 = {**SIMPLE_ENV, "NEW_KEY": "newval"}
    r1 = digest_env(SIMPLE_ENV)
    r2 = digest_env(env2)
    diff = r1.diff_against(r2)
    assert "NEW_KEY" in diff


def test_summary_contains_count():
    report = digest_env(SIMPLE_ENV)
    assert str(len(SIMPLE_ENV)) in report.summary()


# ---------------------------------------------------------------------------
# digest_formatter
# ---------------------------------------------------------------------------

@pytest.fixture
def report():
    return digest_env(SIMPLE_ENV)


def test_format_text_contains_header(report):
    out = format_text(report)
    assert "Digest Report" in out


def test_format_text_contains_all_keys(report):
    out = format_text(report)
    for key in SIMPLE_ENV:
        assert key in out


def test_format_text_contains_fingerprint(report):
    out = format_text(report)
    assert report.fingerprint()[:12] in out


def test_format_json_valid_json(report):
    out = format_json(report)
    data = json.loads(out)
    assert data["algorithm"] == "sha256"
    assert "fingerprint" in data
    assert len(data["entries"]) == len(SIMPLE_ENV)


def test_format_csv_has_header(report):
    out = format_csv(report)
    assert out.startswith("key,checksum,algorithm")


def test_format_csv_row_count(report):
    out = format_csv(report)
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == len(SIMPLE_ENV) + 1  # header + data rows
