"""Export environment variable diffs and validation results to various formats."""

import json
import csv
import io
from typing import Union
from env_guardian.comparator import EnvDiff
from env_guardian.validator import ValidationResult


def _diff_to_dict(diff: EnvDiff) -> dict:
    return {
        "missing_keys": list(diff.missing_keys),
        "extra_keys": list(diff.extra_keys),
        "mismatched_values": {
            k: {"base": v[0], "target": v[1]}
            for k, v in diff.mismatched_values.items()
        },
    }


def _validation_to_dict(result: ValidationResult) -> dict:
    return {
        "valid": result.is_valid,
        "errors": [
            {"key": e.key, "message": e.message}
            for e in result.errors
        ],
    }


def export_json(data: Union[EnvDiff, ValidationResult], indent: int = 2) -> str:
    """Serialize an EnvDiff or ValidationResult to a JSON string."""
    if isinstance(data, EnvDiff):
        payload = _diff_to_dict(data)
    elif isinstance(data, ValidationResult):
        payload = _validation_to_dict(data)
    else:
        raise TypeError(f"Unsupported type for export: {type(data)}")  
    return json.dumps(payload, indent=indent)


def export_csv(diff: EnvDiff) -> str:
    """Serialize an EnvDiff to a CSV string with columns: key, status, base_value, target_value."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["key", "status", "base_value", "target_value"])

    for key in sorted(diff.missing_keys):
        writer.writerow([key, "missing", "", ""])

    for key in sorted(diff.extra_keys):
        writer.writerow([key, "extra", "", ""])

    for key, (base_val, target_val) in sorted(diff.mismatched_values.items()):
        writer.writerow([key, "mismatch", base_val, target_val])

    return output.getvalue()


def export_dotenv(env: dict) -> str:
    """Serialize a plain env dict back to .env file format."""
    lines = []
    for key, value in sorted(env.items()):
        if " " in value or "#" in value or not value:
            value = f'"{value}"'
        lines.append(f"{key}={value}")
    return "\n".join(lines) + ("\n" if lines else "")
