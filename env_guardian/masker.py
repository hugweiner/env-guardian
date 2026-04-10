"""Mask environment variable values for safe display or logging."""

from dataclasses import dataclass, field
from typing import Dict, List

_SENSITIVE_PATTERNS = (
    "secret", "password", "passwd", "token", "api_key", "apikey",
    "auth", "private", "credential", "cert", "key", "pass",
)

DEFAULT_MASK = "***"
DEFAULT_PARTIAL_VISIBLE = 4


@dataclass
class MaskEntry:
    key: str
    original: str
    masked: str
    was_masked: bool

    def __str__(self) -> str:
        status = "masked" if self.was_masked else "visible"
        return f"{self.key}={self.masked} [{status}]"


@dataclass
class MaskReport:
    entries: List[MaskEntry] = field(default_factory=list)

    @property
    def masked_count(self) -> int:
        return sum(1 for e in self.entries if e.was_masked)

    @property
    def visible_count(self) -> int:
        return sum(1 for e in self.entries if not e.was_masked)

    def summary(self) -> str:
        return (
            f"{len(self.entries)} keys: "
            f"{self.masked_count} masked, {self.visible_count} visible"
        )

    def as_dict(self) -> Dict[str, str]:
        return {e.key: e.masked for e in self.entries}


def _is_sensitive(key: str) -> bool:
    lower = key.lower()
    return any(pat in lower for pat in _SENSITIVE_PATTERNS)


def _partial_mask(value: str, visible: int, mask: str) -> str:
    if len(value) <= visible:
        return mask
    return value[:visible] + mask


def mask_env(
    env: Dict[str, str],
    partial: bool = False,
    visible_chars: int = DEFAULT_PARTIAL_VISIBLE,
    mask_token: str = DEFAULT_MASK,
) -> MaskReport:
    """Mask sensitive values in an env dict.

    Args:
        env: The environment variables to process.
        partial: If True, show the first `visible_chars` characters before the mask.
        visible_chars: Number of characters to reveal when partial=True.
        mask_token: The string used to replace (or append to) sensitive values.

    Returns:
        A MaskReport containing all entries with masking applied.
    """
    report = MaskReport()
    for key, value in env.items():
        if _is_sensitive(key):
            masked = _partial_mask(value, visible_chars, mask_token) if partial else mask_token
            report.entries.append(MaskEntry(key=key, original=value, masked=masked, was_masked=True))
        else:
            report.entries.append(MaskEntry(key=key, original=value, masked=value, was_masked=False))
    return report
