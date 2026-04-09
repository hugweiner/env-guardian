"""Redactor module: mask sensitive values in env dicts for safe display/logging."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_DEFAULT_SECRET_PATTERNS = (
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "TOKEN",
    "API_KEY",
    "PRIVATE_KEY",
    "AUTH",
    "CREDENTIAL",
    "CERT",
    "SIGNING",
)

DEFAULT_MASK = "***REDACTED***"


@dataclass
class RedactReport:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def redact_count(self) -> int:
        return len(self.redacted_keys)

    def summary(self) -> str:
        if not self.redacted_keys:
            return "No sensitive keys redacted."
        keys = ", ".join(sorted(self.redacted_keys))
        return f"{self.redact_count} key(s) redacted: {keys}"


def _is_sensitive(key: str, patterns: tuple) -> bool:
    upper = key.upper()
    return any(pattern in upper for pattern in patterns)


def redact_env(
    env: Dict[str, str],
    mask: str = DEFAULT_MASK,
    extra_patterns: Optional[List[str]] = None,
    preserve_empty: bool = True,
) -> RedactReport:
    """Return a RedactReport with sensitive values replaced by mask.

    Args:
        env: The environment dict to redact.
        mask: The string to substitute for sensitive values.
        extra_patterns: Additional substrings that mark a key as sensitive.
        preserve_empty: If True, empty values are kept as-is even for sensitive keys.
    """
    patterns = _DEFAULT_SECRET_PATTERNS
    if extra_patterns:
        patterns = patterns + tuple(p.upper() for p in extra_patterns)

    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if _is_sensitive(key, patterns):
            if preserve_empty and value == "":
                redacted[key] = value
            else:
                redacted[key] = mask
                redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactReport(
        original=dict(env),
        redacted=redacted,
        redacted_keys=redacted_keys,
    )
