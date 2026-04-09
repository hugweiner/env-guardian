"""Environment profiler: classify and summarize env var patterns."""

from dataclasses import dataclass, field
from typing import Dict, List

SECRET_KEYWORDS = ("SECRET", "PASSWORD", "TOKEN", "KEY", "PASS", "PRIVATE", "CREDENTIAL")
URL_KEYWORDS = ("URL", "URI", "HOST", "ENDPOINT", "DSN")
FLAG_KEYWORDS = ("ENABLE", "DISABLE", "FEATURE", "FLAG", "DEBUG", "VERBOSE")


@dataclass
class ProfileEntry:
    key: str
    category: str  # 'secret', 'url', 'flag', 'numeric', 'general'
    is_empty: bool
    value_length: int

    def __str__(self) -> str:
        return f"{self.key} [{self.category}]{'  (empty)' if self.is_empty else ''}"


@dataclass
class ProfileReport:
    entries: List[ProfileEntry] = field(default_factory=list)

    @property
    def by_category(self) -> Dict[str, List[ProfileEntry]]:
        result: Dict[str, List[ProfileEntry]] = {}
        for entry in self.entries:
            result.setdefault(entry.category, []).append(entry)
        return result

    @property
    def empty_count(self) -> int:
        return sum(1 for e in self.entries if e.is_empty)

    @property
    def total(self) -> int:
        return len(self.entries)

    def summary(self) -> str:
        cats = self.by_category
        lines = [f"Total variables : {self.total}", f"Empty values    : {self.empty_count}"]
        for cat, items in sorted(cats.items()):
            lines.append(f"  {cat:<10}: {len(items)}")
        return "\n".join(lines)


def _classify(key: str, value: str) -> str:
    upper = key.upper()
    if any(kw in upper for kw in SECRET_KEYWORDS):
        return "secret"
    if any(kw in upper for kw in URL_KEYWORDS):
        return "url"
    if any(kw in upper for kw in FLAG_KEYWORDS):
        return "flag"
    if value.lstrip("-").isdigit():
        return "numeric"
    return "general"


def profile_env(env: Dict[str, str]) -> ProfileReport:
    """Build a ProfileReport from an env mapping."""
    report = ProfileReport()
    for key, value in env.items():
        category = _classify(key, value)
        report.entries.append(
            ProfileEntry(
                key=key,
                category=category,
                is_empty=(value == ""),
                value_length=len(value),
            )
        )
    return report
