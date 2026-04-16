import pytest
from env_guardian.joiner import join_envs


@pytest.fixture
def env_a():
    return {"DB_HOST": "localhost", "APP_ENV": "dev"}


@pytest.fixture
def env_b():
    return {"DB_HOST": "prod-db", "SECRET_KEY": "abc123"}


def test_join_returns_report(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b})
    assert report is not None


def test_all_keys_present(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b})
    keys = {e.key for e in report.entries}
    assert keys == {"DB_HOST", "APP_ENV", "SECRET_KEY"}


def test_last_wins_strategy(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b}, strategy="last")
    env = report.joined_env()
    assert env["DB_HOST"] == "prod-db"


def test_first_wins_strategy(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b}, strategy="first")
    env = report.joined_env()
    assert env["DB_HOST"] == "localhost"


def test_unique_key_from_single_source(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b})
    env = report.joined_env()
    assert env["APP_ENV"] == "dev"
    assert env["SECRET_KEY"] == "abc123"


def test_sources_tracked_for_conflict(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b})
    entry = next(e for e in report.entries if e.key == "DB_HOST")
    assert "a" in entry.sources
    assert "b" in entry.sources


def test_sources_single_for_unique_key(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b})
    entry = next(e for e in report.entries if e.key == "APP_ENV")
    assert entry.sources == ["a"]


def test_joined_count(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b})
    assert report.joined_count() == 3


def test_summary(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b})
    assert "3" in report.summary()


def test_keys_from(env_a, env_b):
    report = join_envs({"a": env_a, "b": env_b})
    assert "APP_ENV" in report.keys_from("a")
    assert "SECRET_KEY" in report.keys_from("b")


def test_invalid_strategy_raises(env_a):
    with pytest.raises(ValueError, match="Unknown strategy"):
        join_envs({"a": env_a}, strategy="random")


def test_single_env_returns_same_keys():
    env = {"FOO": "bar", "BAZ": "qux"}
    report = join_envs({"only": env})
    assert report.joined_env() == env
