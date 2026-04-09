"""Tests for env_guardian.resolver."""
import pytest

from env_guardian.resolver import resolve_layers


def test_single_layer_resolved():
    report = resolve_layers([("prod", {"A": "1", "B": "2"})])
    env = report.resolved_env()
    assert env == {"A": "1", "B": "2"}


def test_last_layer_wins():
    report = resolve_layers(
        [
            ("base", {"A": "base", "B": "base"}),
            ("prod", {"A": "prod"}),
        ]
    )
    env = report.resolved_env()
    assert env["A"] == "prod"
    assert env["B"] == "base"


def test_base_env_is_lowest_priority():
    report = resolve_layers(
        [("layer", {"X": "layer"})],
        base={"X": "base", "Y": "only_base"},
    )
    env = report.resolved_env()
    assert env["X"] == "layer"
    assert env["Y"] == "only_base"


def test_overridden_keys_detected():
    report = resolve_layers(
        [
            ("base", {"KEY": "v1"}),
            ("override", {"KEY": "v2"}),
        ]
    )
    assert "KEY" in report.overridden_keys()


def test_non_overridden_key_not_in_overridden_list():
    report = resolve_layers(
        [
            ("base", {"ONLY_HERE": "v1"}),
            ("other", {"OTHER_KEY": "v2"}),
        ]
    )
    assert "ONLY_HERE" not in report.overridden_keys()
    assert "OTHER_KEY" not in report.overridden_keys()


def test_summary_contains_layer_names():
    report = resolve_layers([("alpha", {"A": "1"}), ("beta", {"B": "2"})])
    summary = report.summary()
    assert "alpha" in summary
    assert "beta" in summary


def test_empty_layers_returns_empty_env():
    report = resolve_layers([])
    assert report.resolved_env() == {}


def test_layers_attribute_preserved():
    report = resolve_layers([("l1", {}), ("l2", {})])
    assert report.layers == ["l1", "l2"]


def test_entry_source_is_correct():
    report = resolve_layers([("dev", {"PORT": "3000"})])
    entry = next(e for e in report.entries if e.key == "PORT")
    assert entry.source == "dev"
    assert entry.value == "3000"
