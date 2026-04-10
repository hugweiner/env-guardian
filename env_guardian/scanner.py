"""Scanner module: detect hardcoded secrets and suspicious patterns in env values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

# Patterns that suggest a value may be a hardcoded secret or sensitive data
_PATTERNS: List[tuple[str, str]] = [
    ("high", r"(?i)^(sk|pk|rk|ak|ey)[_-]?[0-9a-z]{16,}"),  # API key prefixes
    ("high", r"(?i)^[0-9a-f]{32,64}$"),                    # Hex tokens
    ("high", r"(?i)^[A-Za-z0-9+/]{40,}={0,2}$"),           # Base64-ish blobs
    ("medium", r"(?i)password|passwd|secret|token|apikey|api_key"),  # Key name hints
    ("medium", r"(?i)^https?://[^:]+:[^@]+@"),             # URL with credentials
    ("low", r"(?i)^[0-9]{8,}"),                            # Long numeric sequences
]


@dataclass
class ScanHit:
    key: str
    value: str
    severity: str  # "high" | "medium" | "low"
    reason: str

    def __str__(self) -> str:
        masked = self.value[:4] + "****" if len(self.value) > 4 else "****"
        return f"[{self.severity.upper()}] {self.key}={masked} — {self.reason}"


@dataclass
class ScanReport:
    hits: List[ScanHit] = field(default_factory=list)

    def add(self, hit: ScanHit) -> None:
        self.hits.append(hit)

    @property
    def is_clean(self) -> bool:
        return len(self.hits) == 0

    def by_severity(self, severity: str) -> List[ScanHit]:
        return [h for h in self.hits if h.severity == severity]

    def summary(self) -> str:
        if self.is_clean:
            return "No suspicious values detected."
        counts = {s: len(self.by_severity(s)) for s in ("high", "medium", "low")}
        parts = [f"{v} {k}" for k, v in counts.items() if v]
        return f"{len(self.hits)} hit(s): " + ", ".join(parts)


def scan_env(env: Dict[str, str]) -> ScanReport:
    """Scan an env dict for suspicious or hardcoded secret values."""
    report = ScanReport()
    for key, value in env.items():
        if not value:
            continue
        for severity, pattern in _PATTERNS:
            if re.search(pattern, value) or re.search(pattern, key):
                reason = f"Matches pattern: {pattern}"
                report.add(ScanHit(key=key, value=value, severity=severity, reason=reason))
                break  # one hit per key is enough
    return report
