"""Tests for env_guardian.encryptor."""

import pytest

from env_guardian.encryptor import (
    EncryptReport,
    decrypt_env,
    encrypt_env,
)

PASSPHRASE = "super-secret-passphrase"


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "hunter2",
        "API_KEY": "abc123",
        "PORT": "8080",
        "AUTH_TOKEN": "tok_xyz",
    }


def test_encrypt_returns_report(sample_env):
    report = encrypt_env(sample_env, PASSPHRASE)
    assert isinstance(report, EncryptReport)


def test_sensitive_keys_are_encrypted(sample_env):
    report = encrypt_env(sample_env, PASSPHRASE, sensitive_only=True)
    for k in ("DB_PASSWORD", "API_KEY", "AUTH_TOKEN"):
        assert report.encrypted_env[k].startswith("ENC:")


def test_non_sensitive_keys_unchanged(sample_env):
    report = encrypt_env(sample_env, PASSPHRASE, sensitive_only=True)
    assert report.encrypted_env["APP_NAME"] == "myapp"
    assert report.encrypted_env["PORT"] == "8080"


def test_encrypt_count_matches_sensitive_keys(sample_env):
    report = encrypt_env(sample_env, PASSPHRASE, sensitive_only=True)
    assert report.encrypt_count == 3


def test_encrypted_keys_list_populated(sample_env):
    report = encrypt_env(sample_env, PASSPHRASE, sensitive_only=True)
    assert set(report.encrypted_keys) == {"DB_PASSWORD", "API_KEY", "AUTH_TOKEN"}


def test_encrypt_all_keys_when_not_sensitive_only(sample_env):
    report = encrypt_env(sample_env, PASSPHRASE, sensitive_only=False)
    assert report.encrypt_count == len(sample_env)
    for v in report.encrypted_env.values():
        assert v.startswith("ENC:")


def test_decrypt_restores_original_values(sample_env):
    report = encrypt_env(sample_env, PASSPHRASE, sensitive_only=True)
    decrypted = decrypt_env(report.encrypted_env, PASSPHRASE)
    assert decrypted == sample_env


def test_decrypt_with_wrong_passphrase_gives_wrong_values(sample_env):
    report = encrypt_env(sample_env, PASSPHRASE, sensitive_only=True)
    decrypted = decrypt_env(report.encrypted_env, "wrong-passphrase")
    assert decrypted["DB_PASSWORD"] != sample_env["DB_PASSWORD"]


def test_decrypt_leaves_non_encrypted_values_unchanged(sample_env):
    """Non-ENC: prefixed values should pass through decrypt_env unmodified."""
    report = encrypt_env(sample_env, PASSPHRASE, sensitive_only=True)
    decrypted = decrypt_env(report.encrypted_env, PASSPHRASE)
    assert decrypted["APP_NAME"] == sample_env["APP_NAME"]
    assert decrypted["PORT"] == sample_env["PORT"]


def test_summary_with_encrypted_keys(sample_env):
    report = encrypt_env(sample_env, PASSPHRASE, sensitive_only=True)
    summary = report.summary()
    assert "3 key(s) encrypted" in summary


def test_summary_with_no_encrypted_keys():
    env = {"APP_NAME": "myapp", "PORT": "8080"}
    report = encrypt_env(env, PASSPHRASE, sensitive_only=True)
    assert report.summary() == "No keys were encrypted."


def test_passphrase_hint_stored():
    env = {"SECRET_KEY": "abc"}
    report = encrypt_env(env, PASSPHRASE, passphrase_hint="ask-devops")
    assert report.passphrase_hint == "ask-devops"


def test_passphrase_hint_defaults_to_none():
    """When no hint is provided, passphrase_hint should be None."""
    env = {"SECRET_KEY": "abc"}
    report = encrypt_env(env, PASSPHRASE)
    assert report.passphrase_hint is None


def test_empty_env_produces_empty_report():
    report = encrypt_env({}, PASSPHRASE)
    assert report.encrypted_env == {}
    assert report.encrypt_count == 0
