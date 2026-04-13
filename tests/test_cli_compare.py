"""Tests for the compare CLI command."""
from __future__ import annotations

import json
import os
import tempfile

import pytest
from click.testing import CliRunner

from env_guardian.cli_compare import compare_cmd


@pytest.fixture()
def runner():
    return CliRunner()


def _write_env(path: str, content: str) -> None:
    with open(path, "w") as fh:
        fh.write(content)


def test_compare_clean_exits_zero(runner, tmp_path):
    base = str(tmp_path / "base.env")
    target = str(tmp_path / "target.env")
    _write_env(base, "A=1\nB=2\n")
    _write_env(target, "A=1\nB=2\n")
    result = runner.invoke(compare_cmd, [base, target])
    assert result.exit_code == 0


def test_compare_clean_shows_no_differences(runner, tmp_path):
    base = str(tmp_path / "base.env")
    target = str(tmp_path / "target.env")
    _write_env(base, "A=1\n")
    _write_env(target, "A=1\n")
    result = runner.invoke(compare_cmd, [base, target])
    assert "No differences found." in result.output


def test_compare_dirty_shows_missing(runner, tmp_path):
    base = str(tmp_path / "base.env")
    target = str(tmp_path / "target.env")
    _write_env(base, "A=1\nB=2\n")
    _write_env(target, "A=1\n")
    result = runner.invoke(compare_cmd, [base, target])
    assert "B" in result.output


def test_compare_json_format(runner, tmp_path):
    base = str(tmp_path / "base.env")
    target = str(tmp_path / "target.env")
    _write_env(base, "A=1\n")
    _write_env(target, "A=2\n")
    result = runner.invoke(compare_cmd, [base, target, "--format", "json"])
    data = json.loads(result.output)
    assert "mismatched" in data


def test_compare_csv_format(runner, tmp_path):
    base = str(tmp_path / "base.env")
    target = str(tmp_path / "target.env")
    _write_env(base, "A=1\nB=2\n")
    _write_env(target, "A=1\n")
    result = runner.invoke(compare_cmd, [base, target, "--format", "csv"])
    assert "key,issue" in result.output


def test_compare_exit_code_flag_triggers_on_diff(runner, tmp_path):
    base = str(tmp_path / "base.env")
    target = str(tmp_path / "target.env")
    _write_env(base, "A=1\nB=2\n")
    _write_env(target, "A=1\n")
    result = runner.invoke(compare_cmd, [base, target, "--exit-code"])
    assert result.exit_code == 1


def test_compare_exit_code_flag_zero_when_clean(runner, tmp_path):
    base = str(tmp_path / "base.env")
    target = str(tmp_path / "target.env")
    _write_env(base, "A=1\n")
    _write_env(target, "A=1\n")
    result = runner.invoke(compare_cmd, [base, target, "--exit-code"])
    assert result.exit_code == 0


def test_compare_ignore_values_skips_mismatch(runner, tmp_path):
    base = str(tmp_path / "base.env")
    target = str(tmp_path / "target.env")
    _write_env(base, "A=1\n")
    _write_env(target, "A=different\n")
    result = runner.invoke(compare_cmd, [base, target, "--ignore-values"])
    assert "No differences found." in result.output
