"""Tests for env_guardian.masker."""

import pytest
from env_guardian.masker import mask_env, MaskReport, DEFAULT_MASK


@pytest.fixture
def mixed_env():
    return {
        "APP_NAME": "myapp",
        "DEBUG": "true",
        "SECRET_KEY": "supersecret123",
        "DB_PASSWORD": "hunter2",
        "API_KEY": "abc123xyz",
        "PORT": "8080",
        "AUTH_TOKEN": "tok_abcdef",
    }


def test_mask_env_returns_report(mixed_env):
    report = mask_env(mixed_env)
    assert isinstance(report, MaskReport)


def test_non_sensitive_keys_are_visible(mixed_env):
    report = mask_env(mixed_env)
    visible = {e.key: e.masked for e in report.entries if not e.was_masked}
    assert visible["APP_NAME"] == "myapp"
    assert visible["DEBUG"] == "true"
    assert visible["PORT"] == "8080"


def test_sensitive_keys_are_masked(mixed_env):
    report = mask_env(mixed_env)
    masked_keys = {e.key for e in report.entries if e.was_masked}
    assert "SECRET_KEY" in masked_keys
    assert "DB_PASSWORD" in masked_keys
    assert "API_KEY" in masked_keys
    assert "AUTH_TOKEN" in masked_keys


def test_masked_value_is_mask_token(mixed_env):
    report = mask_env(mixed_env)
    for entry in report.entries:
        if entry.was_masked:
            assert entry.masked == DEFAULT_MASK


def test_masked_count_matches_sensitive_keys(mixed_env):
    report = mask_env(mixed_env)
    assert report.masked_count == 4


def test_visible_count_matches_non_sensitive_keys(mixed_env):
    report = mask_env(mixed_env)
    assert report.visible_count == 3


def test_partial_mask_reveals_prefix(mixed_env):
    report = mask_env(mixed_env, partial=True, visible_chars=3)
    entry = next(e for e in report.entries if e.key == "SECRET_KEY")
    assert entry.masked.startswith("sup")
    assert entry.masked.endswith(DEFAULT_MASK)


def test_partial_mask_short_value_fully_masked():
    env = {"API_KEY": "ab"}
    report = mask_env(env, partial=True, visible_chars=4)
    entry = report.entries[0]
    assert entry.masked == DEFAULT_MASK


def test_custom_mask_token(mixed_env):
    report = mask_env(mixed_env, mask_token="[REDACTED]")
    for entry in report.entries:
        if entry.was_masked:
            assert entry.masked == "[REDACTED]"


def test_as_dict_contains_all_keys(mixed_env):
    report = mask_env(mixed_env)
    result = report.as_dict()
    assert set(result.keys()) == set(mixed_env.keys())


def test_as_dict_sensitive_values_masked(mixed_env):
    report = mask_env(mixed_env)
    result = report.as_dict()
    assert result["SECRET_KEY"] == DEFAULT_MASK
    assert result["APP_NAME"] == "myapp"


def test_summary_string(mixed_env):
    report = mask_env(mixed_env)
    summary = report.summary()
    assert "masked" in summary
    assert "visible" in summary


def test_empty_env_produces_empty_report():
    report = mask_env({})
    assert len(report.entries) == 0
    assert report.masked_count == 0
    assert report.visible_count == 0
