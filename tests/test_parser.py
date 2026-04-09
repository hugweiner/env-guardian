"""Unit tests for env_guardian.parser."""

import textwrap
from pathlib import Path

import pytest

from env_guardian.parser import parse_env_file, parse_env_string


SAMPLE_ENV = textwrap.dedent("""\
    # Database settings
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME="my_database"
    DB_PASSWORD='s3cr3t'

    # App
    APP_ENV=production
    DEBUG=false
    EMPTY_VAR=
""")


def test_parse_env_string_basic():
    result = parse_env_string(SAMPLE_ENV)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"


def test_parse_env_string_strips_double_quotes():
    result = parse_env_string(SAMPLE_ENV)
    assert result["DB_NAME"] == "my_database"


def test_parse_env_string_strips_single_quotes():
    result = parse_env_string(SAMPLE_ENV)
    assert result["DB_PASSWORD"] == "s3cr3t"


def test_parse_env_string_empty_value():
    result = parse_env_string(SAMPLE_ENV)
    assert result["EMPTY_VAR"] == ""


def test_parse_env_string_ignores_comments():
    result = parse_env_string(SAMPLE_ENV)
    assert all(not k.startswith("#") for k in result)


def test_parse_env_string_key_count():
    result = parse_env_string(SAMPLE_ENV)
    assert len(result) == 7


def test_parse_env_file_success(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("FOO=bar\nBAZ=qux\n")
    result = parse_env_file(env_file)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_env_file_not_found(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "nonexistent.env")


def test_parse_env_string_inline_comment_not_stripped():
    """Values with inline # are kept as-is (not treated as comments)."""
    result = parse_env_string("COLOR=blue # primary")
    assert result["COLOR"] == "blue # primary"
