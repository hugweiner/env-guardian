"""Annotate environment variables with inline comments/descriptions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AnnotationEntry:
    key: str
    value: str
    annotation: Optional[str]

    def __str__(self) -> str:
        tag = f" # {self.annotation}" if self.annotation else ""
        return f"{self.key}={self.value}{tag}"


@dataclass
class AnnotateReport:
    entries: List[AnnotationEntry] = field(default_factory=list)

    def add(self, entry: AnnotationEntry) -> None:
        self.entries.append(entry)

    def annotated_count(self) -> int:
        return sum(1 for e in self.entries if e.annotation is not None)

    def unannotated_count(self) -> int:
        return sum(1 for e in self.entries if e.annotation is None)

    def by_key(self) -> Dict[str, AnnotationEntry]:
        return {e.key: e for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        annotated = self.annotated_count()
        return f"{annotated}/{total} keys annotated"


_BUILTIN_ANNOTATIONS: Dict[str, str] = {
    "DATABASE_URL": "Connection string for the primary database",
    "REDIS_URL": "Connection string for Redis cache",
    "SECRET_KEY": "Secret key used for cryptographic signing",
    "DEBUG": "Enable or disable debug mode",
    "PORT": "Port the application listens on",
    "HOST": "Hostname or IP address to bind to",
    "LOG_LEVEL": "Logging verbosity level (DEBUG, INFO, WARNING, ERROR)",
    "API_KEY": "API key for external service authentication",
    "ALLOWED_HOSTS": "Comma-separated list of allowed hostnames",
    "SENTRY_DSN": "Sentry DSN for error tracking",
}


def annotate_env(
    env: Dict[str, str],
    annotations: Optional[Dict[str, str]] = None,
    use_builtins: bool = True,
) -> AnnotateReport:
    """Annotate each key in *env* using provided and/or built-in annotations."""
    merged: Dict[str, str] = {}
    if use_builtins:
        merged.update(_BUILTIN_ANNOTATIONS)
    if annotations:
        merged.update(annotations)

    report = AnnotateReport()
    for key, value in sorted(env.items()):
        note = merged.get(key)
        report.add(AnnotationEntry(key=key, value=value, annotation=note))
    return report
