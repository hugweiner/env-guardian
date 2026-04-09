"""Tests for env_guardian.exporter module."""

import json
import pytest
from env_guardian.comparator import EnvDiff
from env_guardian.validator import ValidationResult, ValidationError
from env_guardian.exporter import export_json, export_csv, export_dotenv


@pytest.fixture
def sample_diff():
    diff = EnvDiff()
    diff.missing_keys = {"DB_HOST"}
    diff.extra_keys = {"OLD_KEY"}
    diff.mismatched_values = {"LOG_LEVEL": ("debug", "info")}
    return diff


@pytest.fixture
def clean_diff():
    return EnvDiff()


@pytest.fixture
def sample_result():
    result = ValidationResult()
    result.add_error(ValidationError(key="SECRET", message="must not be empty"))
    return result


def test_export_json_diff(sample_diff):
    output = export_json(sample_diff)
    data = json.loads(output)
    assert "DB_HOST" in data["missing_keys"]
    assert "OLD_KEY" in data["extra_keys"]
    assert data["mismatched_values"]["LOG_LEVEL"]["base"] == "debug"
    assert data["mismatched_values"]["LOG_LEVEL"]["target"] == "info"


def test_export_json_clean_diff(clean_diff):
    output = export_json(clean_diff)
    data = json.loads(output)
    assert data["missing_keys"] == []
    assert data["extra_keys"] == []
    assert data["mismatched_values"] == {}


def test_export_json_validation_result(sample_result):
    output = export_json(sample_result)
    data = json.loads(output)
    assert data["valid"] is False
    assert len(data["errors"]) == 1
    assert data["errors"][0]["key"] == "SECRET"


def test_export_json_raises_on_unsupported_type():
    with pytest.raises(TypeError):
        export_json({"key": "value"})


def test_export_csv_contains_headers(sample_diff):
    output = export_csv(sample_diff)
    assert output.startswith("key,status,base_value,target_value")


def test_export_csv_missing_key(sample_diff):
    output = export_csv(sample_diff)
    assert "DB_HOST,missing" in output


def test_export_csv_extra_key(sample_diff):
    output = export_csv(sample_diff)
    assert "OLD_KEY,extra" in output


def test_export_csv_mismatch(sample_diff):
    output = export_csv(sample_diff)
    assert "LOG_LEVEL,mismatch,debug,info" in output


def test_export_dotenv_basic():
    env = {"APP_ENV": "production", "PORT": "8080"}
    output = export_dotenv(env)
    assert "APP_ENV=production" in output
    assert "PORT=8080" in output


def test_export_dotenv_quotes_values_with_spaces():
    env = {"GREETING": "hello world"}
    output = export_dotenv(env)
    assert 'GREETING="hello world"' in output


def test_export_dotenv_quotes_empty_values():
    env = {"EMPTY": ""}
    output = export_dotenv(env)
    assert 'EMPTY=""' in output
