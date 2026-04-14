"""Tests for env_guardian.cloner."""
import pytest

from env_guardian.cloner import clone_env


@pytest.fixture()
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_URL": "redis://localhost",
        "secret_key": "abc123",
    }


def test_clone_returns_report(base_env):
    report = clone_env(base_env)
    assert report is not None


def test_clone_all_keys_present(base_env):
    report = clone_env(base_env)
    assert set(report.cloned_env.keys()) == set(base_env.keys())


def test_clone_values_preserved(base_env):
    report = clone_env(base_env)
    for k, v in base_env.items():
        assert report.cloned_env[k] == v


def test_clone_with_prefix(base_env):
    report = clone_env(base_env, prefix="COPY_")
    for key in report.cloned_env:
        assert key.startswith("COPY_")


def test_clone_prefix_preserves_values(base_env):
    report = clone_env(base_env, prefix="COPY_")
    assert report.cloned_env["COPY_DB_HOST"] == "localhost"


def test_clone_strip_prefix_removes_prefix():
    env = {"PROD_HOST": "example.com", "PROD_PORT": "443"}
    report = clone_env(env, strip_prefix="PROD_")
    assert "HOST" in report.cloned_env
    assert "PORT" in report.cloned_env


def test_clone_strip_prefix_original_key_absent():
    env = {"PROD_HOST": "example.com"}
    report = clone_env(env, strip_prefix="PROD_")
    assert "PROD_HOST" not in report.cloned_env


def test_clone_strip_prefix_empty_result_skipped_with_warning():
    env = {"PREFIX": "value"}
    report = clone_env(env, strip_prefix="PREFIX")
    assert "PREFIX" not in report.cloned_env
    assert len(report.warnings) == 1
    assert report.warnings[0].key == "PREFIX"


def test_clone_uppercase_keys(base_env):
    report = clone_env(base_env, uppercase_keys=True)
    for key in report.cloned_env:
        assert key == key.upper()


def test_clone_uppercase_preserves_values(base_env):
    report = clone_env(base_env, uppercase_keys=True)
    assert report.cloned_env["SECRET_KEY"] == "abc123"


def test_clone_exclude_keys(base_env):
    report = clone_env(base_env, exclude_keys=["DB_HOST", "DB_PORT"])
    assert "DB_HOST" not in report.cloned_env
    assert "DB_PORT" not in report.cloned_env


def test_clone_exclude_does_not_remove_other_keys(base_env):
    report = clone_env(base_env, exclude_keys=["DB_HOST"])
    assert "REDIS_URL" in report.cloned_env


def test_clone_clean_report_no_warnings(base_env):
    report = clone_env(base_env)
    assert report.is_clean()


def test_clone_summary_contains_key_count(base_env):
    report = clone_env(base_env)
    assert str(len(base_env)) in report.summary()


def test_clone_collision_produces_warning():
    # Both PROD_HOST and DEV_HOST map to HOST after strip
    env = {"PROD_HOST": "prod.example.com", "DEV_HOST": "dev.example.com"}
    report = clone_env(env, strip_prefix="PROD_", uppercase_keys=False)
    # Only PROD_HOST is stripped; DEV_HOST stays as-is — no collision here.
    # Force a collision via prefix + existing key:
    env2 = {"A": "1", "PREFIX_A": "2"}
    report2 = clone_env(env2, prefix="PREFIX_")
    assert not report2.is_clean()
    assert any(w.key in ("A", "PREFIX_A") for w in report2.warnings)
