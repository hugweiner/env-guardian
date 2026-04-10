"""Tests for env_guardian.pinner."""

import json
import pytest

from env_guardian.pinner import (
    PinEntry,
    PinReport,
    _checksum,
    check_pins,
    create_pinfile,
    dump_pinfile,
    load_pinfile,
)


@pytest.fixture
def base_env():
    return {"APP_KEY": "secret123", "DEBUG": "false", "PORT": "8080"}


def test_create_pinfile_contains_all_keys(base_env):
    pinfile = create_pinfile(base_env)
    assert set(pinfile.keys()) == set(base_env.keys())


def test_create_pinfile_stores_checksums(base_env):
    pinfile = create_pinfile(base_env)
    for key, value in base_env.items():
        assert pinfile[key] == _checksum(value)


def test_check_pins_clean_when_no_changes(base_env):
    pinfile = create_pinfile(base_env)
    report = check_pins(base_env, pinfile)
    assert report.is_clean()
    assert report.summary() == "No drift detected."


def test_check_pins_detects_drifted_value(base_env):
    pinfile = create_pinfile(base_env)
    modified_env = {**base_env, "APP_KEY": "changed_value"}
    report = check_pins(modified_env, pinfile)
    assert "APP_KEY" in report.drifted
    assert not report.is_clean()


def test_check_pins_detects_new_key(base_env):
    pinfile = create_pinfile(base_env)
    extended_env = {**base_env, "NEW_VAR": "hello"}
    report = check_pins(extended_env, pinfile)
    assert "NEW_VAR" in report.new_keys
    assert not report.is_clean()


def test_check_pins_detects_removed_key(base_env):
    pinfile = create_pinfile(base_env)
    reduced_env = {k: v for k, v in base_env.items() if k != "PORT"}
    report = check_pins(reduced_env, pinfile)
    assert "PORT" in report.removed_keys
    assert not report.is_clean()


def test_summary_lists_all_drift_types(base_env):
    pinfile = create_pinfile(base_env)
    modified = {"APP_KEY": "new_secret", "EXTRA": "extra_val"}
    report = check_pins(modified, pinfile)
    summary = report.summary()
    assert "drifted" in summary
    assert "new" in summary
    assert "removed" in summary


def test_entries_populated_for_all_current_keys(base_env):
    pinfile = create_pinfile(base_env)
    report = check_pins(base_env, pinfile)
    entry_keys = {e.key for e in report.entries}
    assert entry_keys == set(base_env.keys())


def test_dump_and_load_pinfile_roundtrip(base_env):
    pinfile = create_pinfile(base_env)
    serialized = dump_pinfile(pinfile)
    loaded = load_pinfile(serialized)
    assert loaded == pinfile


def test_dump_pinfile_is_valid_json(base_env):
    pinfile = create_pinfile(base_env)
    serialized = dump_pinfile(pinfile)
    parsed = json.loads(serialized)
    assert isinstance(parsed, dict)


def test_pin_entry_str_shows_truncated_checksum():
    entry = PinEntry(key="MY_KEY", value="val", checksum="abcdef1234567890")
    result = str(entry)
    assert "MY_KEY" in result
    assert "abcdef12" in result
