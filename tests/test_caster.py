"""Tests for env_guardian.caster."""
import pytest

from env_guardian.caster import CastEntry, CastReport, cast_env, _infer_and_cast


def test_cast_env_returns_report():
    env = {"PORT": "8080"}
    report = cast_env(env)
    assert isinstance(report, CastReport)
    assert len(report.entries) == 1


def test_integer_value_cast_correctly():
    cast_val, type_name = _infer_and_cast("42")
    assert cast_val == 42
    assert type_name == "int"


def test_float_value_cast_correctly():
    cast_val, type_name = _infer_and_cast("3.14")
    assert cast_val == pytest.approx(3.14)
    assert type_name == "float"


def test_true_cast_to_bool():
    cast_val, type_name = _infer_and_cast("true")
    assert cast_val is True
    assert type_name == "bool"


def test_false_cast_to_bool():
    cast_val, type_name = _infer_and_cast("FALSE")
    assert cast_val is False
    assert type_name == "bool"


def test_csv_value_cast_to_list():
    cast_val, type_name = _infer_and_cast("a,b,c")
    assert cast_val == ["a", "b", "c"]
    assert type_name == "list"


def test_plain_string_stays_str():
    cast_val, type_name = _infer_and_cast("hello")
    assert cast_val == "hello"
    assert type_name == "str"


def test_by_type_filters_correctly():
    env = {"PORT": "8080", "DEBUG": "true", "NAME": "app"}
    report = cast_env(env)
    ints = report.by_type("int")
    assert len(ints) == 1
    assert ints[0].key == "PORT"


def test_type_names_returns_unique_sorted():
    env = {"PORT": "8080", "DEBUG": "true", "NAME": "app"}
    report = cast_env(env)
    names = report.type_names()
    assert names == sorted(set(names))
    assert "int" in names
    assert "bool" in names
    assert "str" in names


def test_as_dict_returns_cast_values():
    env = {"PORT": "9000", "ENABLED": "true"}
    report = cast_env(env)
    d = report.as_dict()
    assert d["PORT"] == 9000
    assert d["ENABLED"] is True


def test_summary_contains_key_count():
    env = {"A": "1", "B": "hello"}
    report = cast_env(env)
    summary = report.summary()
    assert "2 keys" in summary


def test_list_items_stripped_of_whitespace():
    cast_val, type_name = _infer_and_cast("x , y , z")
    assert cast_val == ["x", "y", "z"]
    assert type_name == "list"
