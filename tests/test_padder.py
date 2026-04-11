"""Tests for env_guardian.padder."""

import pytest

from env_guardian.padder import pad_env


@pytest.fixture
def short_env():
    return {
        "TOKEN": "abc",
        "SECRET": "xy",
        "LONG_VALUE": "already_long_enough",
    }


def test_clean_env_produces_no_warnings():
    env = {"KEY": "long_enough_value"}
    report = pad_env(env, min_length=4)
    assert report.is_clean()


def test_short_value_is_padded(short_env):
    report = pad_env(short_env, min_length=8)
    assert report.env["TOKEN"] == "00000abc"


def test_padded_count_correct(short_env):
    report = pad_env(short_env, min_length=8)
    # TOKEN (3) and SECRET (2) are short; LONG_VALUE is fine
    assert report.padded_count() == 2


def test_long_value_unchanged(short_env):
    report = pad_env(short_env, min_length=8)
    assert report.env["LONG_VALUE"] == "already_long_enough"


def test_right_align_pads_on_left():
    env = {"PORT": "80"}
    report = pad_env(env, min_length=6, fill_char="0", align="right")
    assert report.env["PORT"] == "000080"


def test_left_align_pads_on_right():
    env = {"PORT": "80"}
    report = pad_env(env, min_length=6, fill_char="-", align="left")
    assert report.env["PORT"] == "80----"


def test_custom_fill_char():
    env = {"KEY": "hi"}
    report = pad_env(env, min_length=5, fill_char="*", align="right")
    assert report.env["KEY"] == "***hi"


def test_keys_filter_restricts_padding():
    env = {"A": "x", "B": "y", "C": "z"}
    report = pad_env(env, min_length=4, fill_char="0", keys=["A"])
    assert report.env["A"] == "000x"
    assert report.env["B"] == "y"
    assert report.env["C"] == "z"
    assert report.padded_count() == 1


def test_warning_contains_original_and_padded():
    env = {"SECRET": "ab"}
    report = pad_env(env, min_length=5)
    assert len(report.warnings) == 1
    w = report.warnings[0]
    assert w.original == "ab"
    assert w.padded == "000ab"
    assert w.key == "SECRET"


def test_invalid_fill_char_raises():
    with pytest.raises(ValueError, match="fill_char"):
        pad_env({"K": "v"}, fill_char="ab")


def test_invalid_align_raises():
    with pytest.raises(ValueError, match="align"):
        pad_env({"K": "v"}, align="center")


def test_summary_clean():
    report = pad_env({"KEY": "long_enough"}, min_length=4)
    assert "No padding" in report.summary()


def test_summary_dirty():
    report = pad_env({"KEY": "x"}, min_length=4)
    assert "1 value(s) padded" in report.summary()
