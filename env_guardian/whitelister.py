"""Whitelister: filter env vars to only those whose keys are in an allowed set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class WhitelistEntry:
    key: str
    value: str
    allowed: bool
    reason: Optional[str] = None

    def __str__(self) -> str:  # pragma: no cover
        status = "allowed" if self.allowed else "blocked"
        return f"{self.key}={self.value!r} [{status}]"


@dataclass
class WhitelistReport:
    entries: List[WhitelistEntry] = field(default_factory=list)

    def add(self, entry: WhitelistEntry) -> None:
        self.entries.append(entry)

    @property
    def allowed_count(self) -> int:
        return sum(1 for e in self.entries if e.allowed)

    @property
    def blocked_count(self) -> int:
        return sum(1 for e in self.entries if not e.allowed)

    @property
    def allowed_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries if e.allowed}

    def is_clean(self) -> bool:
        """True when every key in the env was on the whitelist."""
        return self.blocked_count == 0

    def summary(self) -> str:
        total = len(self.entries)
        return (
            f"{self.allowed_count}/{total} keys allowed, "
            f"{self.blocked_count} blocked"
        )


def whitelist_env(
    env: Dict[str, str],
    allowed_keys: List[str],
    *,
    case_sensitive: bool = True,
) -> WhitelistReport:
    """Return a WhitelistReport indicating which keys are allowed or blocked.

    Args:
        env: The environment mapping to filter.
        allowed_keys: Keys that are permitted.
        case_sensitive: When False, comparison is done in upper-case.
    """
    report = WhitelistReport()

    if case_sensitive:
        allowed_set = set(allowed_keys)
    else:
        allowed_set = {k.upper() for k in allowed_keys}

    for key, value in env.items():
        compare_key = key if case_sensitive else key.upper()
        if compare_key in allowed_set:
            report.add(WhitelistEntry(key=key, value=value, allowed=True))
        else:
            report.add(
                WhitelistEntry(
                    key=key,
                    value=value,
                    allowed=False,
                    reason="key not in whitelist",
                )
            )

    return report
