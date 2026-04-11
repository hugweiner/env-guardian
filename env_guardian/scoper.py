"""Scope env vars by environment name (e.g. PROD_*, DEV_*, STAGING_*)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeEntry:
    key: str
    value: str
    scope: str
    original_key: str

    def __str__(self) -> str:
        return f"[{self.scope}] {self.original_key} -> {self.key}={self.value}"


@dataclass
class ScopeReport:
    entries: List[ScopeEntry] = field(default_factory=list)
    unscoped: Dict[str, str] = field(default_factory=dict)

    def add(self, entry: ScopeEntry) -> None:
        self.entries.append(entry)

    def by_scope(self, scope: str) -> List[ScopeEntry]:
        return [e for e in self.entries if e.scope == scope]

    def scope_names(self) -> List[str]:
        seen: List[str] = []
        for e in self.entries:
            if e.scope not in seen:
                seen.append(e.scope)
        return seen

    def scoped_env(self, scope: str) -> Dict[str, str]:
        """Return a flat env dict for the given scope, keys stripped of prefix."""
        return {e.key: e.value for e in self.by_scope(scope)}

    def summary(self) -> str:
        total = len(self.entries)
        unscoped = len(self.unscoped)
        scopes = self.scope_names()
        return (
            f"{total} scoped entries across {len(scopes)} scope(s); "
            f"{unscoped} unscoped key(s)"
        )


def scope_env(
    env: Dict[str, str],
    scopes: List[str],
    *,
    separator: str = "_",
    strip_prefix: bool = True,
    case_sensitive: bool = False,
) -> ScopeReport:
    """Partition *env* into scopes based on key prefixes.

    Args:
        env: flat mapping of key -> value.
        scopes: ordered list of scope names to recognise (e.g. ["PROD", "DEV"]).
        separator: character that separates the scope prefix from the rest of the key.
        strip_prefix: when True the scope prefix + separator are removed from the key.
        case_sensitive: when False scope matching is case-insensitive.
    """
    report = ScopeReport()
    normalised_scopes = scopes if case_sensitive else [s.upper() for s in scopes]

    for original_key, value in env.items():
        compare_key = original_key if case_sensitive else original_key.upper()
        matched_scope: Optional[str] = None

        for scope in normalised_scopes:
            prefix = scope + separator
            if compare_key.startswith(prefix):
                matched_scope = scope
                break

        if matched_scope is None:
            report.unscoped[original_key] = value
            continue

        if strip_prefix:
            prefix_len = len(matched_scope) + len(separator)
            stripped_key = original_key[prefix_len:]
        else:
            stripped_key = original_key

        report.add(ScopeEntry(
            key=stripped_key,
            value=value,
            scope=matched_scope,
            original_key=original_key,
        ))

    return report
