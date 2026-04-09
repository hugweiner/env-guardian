"""Validator module for checking environment variable rules and constraints."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class ValidationError:
    key: str
    message: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.message}"


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, key: str, message: str) -> None:
        self.errors.append(ValidationError(key=key, message=message))

    def summary(self) -> str:
        if self.is_valid:
            return "All validations passed."
        lines = [f"{len(self.errors)} validation error(s) found:"]
        for err in self.errors:
            lines.append(f"  - {err}")
        return "\n".join(lines)


def validate_env(
    env: Dict[str, str],
    required_keys: Optional[List[str]] = None,
    pattern_rules: Optional[Dict[str, str]] = None,
    non_empty_keys: Optional[List[str]] = None,
) -> ValidationResult:
    """Validate an environment variable dict against a set of rules.

    Args:
        env: Parsed environment variables as a dict.
        required_keys: Keys that must be present in env.
        pattern_rules: Mapping of key -> regex pattern the value must match.
        non_empty_keys: Keys whose values must not be empty strings.

    Returns:
        A ValidationResult containing any errors found.
    """
    result = ValidationResult()

    if required_keys:
        for key in required_keys:
            if key not in env:
                result.add_error(key, "Required key is missing.")

    if non_empty_keys:
        for key in non_empty_keys:
            if key in env and env[key].strip() == "":
                result.add_error(key, "Value must not be empty.")

    if pattern_rules:
        for key, pattern in pattern_rules.items():
            if key in env:
                if not re.fullmatch(pattern, env[key]):
                    result.add_error(
                        key,
                        f"Value '{env[key]}' does not match required pattern '{pattern}'.",
                    )

    return result
