"""Tests for env_guardian.redactor."""

import pytest
from env_guardian.redactor import redact_env, DEFAULT_MASK, RedactReport


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "API_KEY": "abc123",
        "PORT": "8080",
        "AUTH_TOKEN": "tok_xyz",
        "DEBUG": "true",
    }


def test_non_sensitive_keys_unchanged(sample_env):
    report = redact_env(sample_env)
    assert report.redacted["APP_NAME"] == "myapp"
    assert report.redacted["PORT"] == "8080"
    assert report.redacted["DEBUG"] == "true"


def test_sensitive_keys_masked(sample_env):
    report = redact_env(sample_env)
    assert report.redacted["DB_PASSWORD"] == DEFAULT_MASK
    assert report.redacted["API_KEY"] == DEFAULT_MASK
    assert report.redacted["AUTH_TOKEN"] == DEFAULT_MASK


def test_redacted_keys_list_populated(sample_env):
    report = redact_env(sample_env)
    assert "DB_PASSWORD" in report.redacted_keys
    assert "API_KEY" in report.redacted_keys
    assert "AUTH_TOKEN" in report.redacted_keys
    assert "APP_NAME" not in report.redacted_keys


def test_redact_count(sample_env):
    report = redact_env(sample_env)
    assert report.redact_count == 3


def test_original_env_unchanged(sample_env):
    report = redact_env(sample_env)
    assert report.original["DB_PASSWORD"] == "s3cr3t"
    assert report.original["API_KEY"] == "abc123"


def test_custom_mask(sample_env):
    report = redact_env(sample_env, mask="[HIDDEN]")
    assert report.redacted["DB_PASSWORD"] == "[HIDDEN]"


def test_preserve_empty_true_keeps_empty_sensitive_value():
    env = {"DB_PASSWORD": "", "APP_NAME": "x"}
    report = redact_env(env, preserve_empty=True)
    assert report.redacted["DB_PASSWORD"] == ""
    assert "DB_PASSWORD" not in report.redacted_keys


def test_preserve_empty_false_masks_empty_sensitive_value():
    env = {"DB_PASSWORD": "", "APP_NAME": "x"}
    report = redact_env(env, preserve_empty=False)
    assert report.redacted["DB_PASSWORD"] == DEFAULT_MASK
    assert "DB_PASSWORD" in report.redacted_keys


def test_extra_patterns_used():
    env = {"MY_CUSTOM_STUFF": "value123", "NORMAL": "ok"}
    report = redact_env(env, extra_patterns=["CUSTOM"])
    assert report.redacted["MY_CUSTOM_STUFF"] == DEFAULT_MASK
    assert report.redacted["NORMAL"] == "ok"


def test_summary_with_no_redactions():
    report = redact_env({"PORT": "8080", "HOST": "localhost"})
    assert report.summary() == "No sensitive keys redacted."


def test_summary_with_redactions(sample_env):
    report = redact_env(sample_env)
    summary = report.summary()
    assert "3 key(s) redacted" in summary
    assert "API_KEY" in summary


def test_clean_env_returns_empty_redacted_keys():
    env = {"HOST": "localhost", "PORT": "5432"}
    report = redact_env(env)
    assert report.redacted_keys == []
    assert report.redact_count == 0
