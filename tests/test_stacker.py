"""Tests for env_guardian.stacker and env_guardian.stack_formatter."""
import json
import pytest

from env_guardian.stacker import stack_envs, StackReport
from env_guardian.stack_formatter import format_text, format_json, format_csv


# ---------------------------------------------------------------------------
# stack_envs
# ---------------------------------------------------------------------------

def test_single_layer_resolves_all_keys():
    env = {"A": "1", "B": "2"}
    report = stack_envs([env], layer_names=["base"])
    assert len(report.entries) == 2


def test_last_layer_wins():
    base = {"KEY": "base_val"}
    override = {"KEY": "override_val"}
    report = stack_envs([base, override], layer_names=["base", "override"])
    entry = report.by_key("KEY")
    assert entry is not None
    assert entry.value == "override_val"
    assert entry.winning_layer == "override"


def test_key_only_in_base_uses_base():
    base = {"ONLY_BASE": "hello"}
    top = {"OTHER": "world"}
    report = stack_envs([base, top], layer_names=["base", "top"])
    entry = report.by_key("ONLY_BASE")
    assert entry is not None
    assert entry.winning_layer == "base"


def test_all_keys_collected_across_layers():
    a = {"X": "1"}
    b = {"Y": "2"}
    c = {"Z": "3"}
    report = stack_envs([a, b, c], layer_names=["a", "b", "c"])
    keys = {e.key for e in report.entries}
    assert keys == {"X", "Y", "Z"}


def test_overridden_count_correct():
    base = {"A": "1", "B": "2"}
    top = {"A": "99"}
    report = stack_envs([base, top], layer_names=["base", "top"])
    assert report.overridden_count() == 1


def test_resolved_env_returns_dict():
    base = {"A": "1", "B": "2"}
    top = {"B": "99"}
    report = stack_envs([base, top], layer_names=["base", "top"])
    env = report.resolved_env()
    assert env["A"] == "1"
    assert env["B"] == "99"


def test_mismatched_layer_names_raises():
    with pytest.raises(ValueError):
        stack_envs([{"A": "1"}], layer_names=["x", "y"])


def test_default_layer_names_generated():
    report = stack_envs([{"A": "1"}, {"B": "2"}])
    assert report.layer_names == ["layer0", "layer1"]


# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------

def test_format_text_contains_header():
    report = stack_envs([{"A": "1"}], layer_names=["base"])
    out = format_text(report)
    assert "Env Stack Report" in out


def test_format_text_shows_winning_layer():
    report = stack_envs([{"KEY": "v"}], layer_names=["prod"])
    out = format_text(report)
    assert "prod" in out


def test_format_text_marks_overridden_key():
    report = stack_envs([{"K": "a"}, {"K": "b"}], layer_names=["base", "top"])
    out = format_text(report)
    assert "[overridden]" in out


def test_format_text_empty_env():
    report = stack_envs([], layer_names=[])
    out = format_text(report)
    assert "(no keys)" in out


# ---------------------------------------------------------------------------
# format_json
# ---------------------------------------------------------------------------

def test_format_json_valid_json():
    report = stack_envs([{"A": "1"}], layer_names=["base"])
    data = json.loads(format_json(report))
    assert "entries" in data
    assert "layers" in data


def test_format_json_entry_has_winning_layer():
    report = stack_envs([{"X": "10"}, {"X": "20"}], layer_names=["l1", "l2"])
    data = json.loads(format_json(report))
    entry = next(e for e in data["entries"] if e["key"] == "X")
    assert entry["winning_layer"] == "l2"


# ---------------------------------------------------------------------------
# format_csv
# ---------------------------------------------------------------------------

def test_format_csv_has_header_row():
    report = stack_envs([{"A": "1"}], layer_names=["base"])
    out = format_csv(report)
    assert "key" in out.splitlines()[0]
    assert "winning_layer" in out.splitlines()[0]


def test_format_csv_row_count():
    report = stack_envs([{"A": "1", "B": "2"}], layer_names=["base"])
    rows = [r for r in format_csv(report).splitlines() if r]
    assert len(rows) == 3  # header + 2 keys
