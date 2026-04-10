"""Tag environment variables with custom labels for grouping and filtering."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TagEntry:
    key: str
    value: str
    tags: List[str] = field(default_factory=list)

    def __str__(self) -> str:
        tag_str = ", ".join(self.tags) if self.tags else "(none)"
        return f"{self.key}={self.value!r} [{tag_str}]"


@dataclass
class TagReport:
    entries: List[TagEntry] = field(default_factory=list)

    def by_tag(self, tag: str) -> List[TagEntry]:
        """Return all entries that have the given tag."""
        return [e for e in self.entries if tag in e.tags]

    def tag_names(self) -> List[str]:
        """Return sorted list of all unique tags used."""
        tags: set = set()
        for entry in self.entries:
            tags.update(entry.tags)
        return sorted(tags)

    def untagged(self) -> List[TagEntry]:
        """Return entries with no tags assigned."""
        return [e for e in self.entries if not e.tags]

    def summary(self) -> str:
        total = len(self.entries)
        untagged = len(self.untagged())
        tag_count = len(self.tag_names())
        return f"{total} keys, {tag_count} unique tags, {untagged} untagged"


_DEFAULT_RULES: Dict[str, List[str]] = {
    "secret": ["SECRET", "PASSWORD", "PASSWD", "TOKEN", "API_KEY", "PRIVATE"],
    "database": ["DB_", "DATABASE", "POSTGRESMONGO", "REDIS"],
    "url": ["URL", "HOST", "ENDPOINT", "DOMAIN"],
    "feature_flag": ["ENABLE_", "DISABLE_", "FEATURE_", "FLAG_"],
    "infra": ["PORT", "TIMEOUT", "WORKERS", "REPLICAS", "MAX_", "MIN_"],
}


def _auto_tags(key: str, rules: Dict[str, List[str]]) -> List[str]:
    upper = key.upper()
    matched = []
    for tag, patterns in rules.items():
        if any(p in upper for p in patterns):
            matched.append(tag)
    return matched


def tag_env(
    env: Dict[str, str],
    extra_rules: Optional[Dict[str, List[str]]] = None,
    manual, List[str]]] = None,
) -> TagReport:
    """Tag each key in env using built-in rules, optional extra rules, and manual overrides."""
    rules = dict(_DEFAULT_RULES)
    if extra_rules:
        for tag, patterns in extra_rules.items():
            rules.setdefault(tag, []).extend(patterns)

    report = TagReport()
    for key, value in env.items():
        tags = _auto_tags(key, rules)
        if manual_tags and key in manual_tags:
            for t in manual_tags[key]:
                if t not in tags:
                    tags.append(t)
        report.entries.append(TagEntry(key=key, value=value, tags=sorted(tags)))
    return report
