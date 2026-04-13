"""Inject key-value pairs into an existing env dict with conflict tracking."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class InjectEntry:
    key: str
    value: str
    overwritten: bool
    previous_value: Optional[str] = None

    def __str__(self) -> str:
        if self.overwritten:
            return f"{self.key} (overwritten: {self.previous_value!r} -> {self.value!r})"
        return f"{self.key}={self.value!r} (new)"


@dataclass
class InjectReport:
    entries: List[InjectEntry] = field(default_factory=list)
    result_env: Dict[str, str] = field(default_factory=dict)

    def add(self, entry: InjectEntry) -> None:
        self.entries.append(entry)

    @property
    def injected_count(self) -> int:
        return len([e for e in self.entries if not e.overwritten])

    @property
    def overwritten_count(self) -> int:
        return len([e for e in self.entries if e.overwritten])

    def is_clean(self) -> bool:
        return self.overwritten_count == 0

    def summary(self) -> str:
        return (
            f"{self.injected_count} key(s) injected, "
            f"{self.overwritten_count} key(s) overwritten."
        )


def inject_env(
    base: Dict[str, str],
    additions: Dict[str, str],
    overwrite: bool = True,
) -> InjectReport:
    """Inject *additions* into *base*, returning an InjectReport.

    Args:
        base: The original environment dict.
        additions: Key-value pairs to inject.
        overwrite: When True (default) existing keys are overwritten;
                   when False they are skipped.
    """
    report = InjectReport(result_env=dict(base))

    for key, value in additions.items():
        if key in report.result_env:
            if overwrite:
                entry = InjectEntry(
                    key=key,
                    value=value,
                    overwritten=True,
                    previous_value=report.result_env[key],
                )
                report.result_env[key] = value
            else:
                entry = InjectEntry(
                    key=key,
                    value=report.result_env[key],
                    overwritten=False,
                    previous_value=report.result_env[key],
                )
        else:
            entry = InjectEntry(key=key, value=value, overwritten=False)
            report.result_env[key] = value

        report.add(entry)

    return report
