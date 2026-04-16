"""Pruner: remove keys matching patterns or predicates from an env dict."""
from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Dict, List, Optional


@dataclass
class PruneEntry:
    key: str
    value: str
    pruned: bool
    reason: Optional[str] = None

    def __str__(self) -> str:
        tag = "pruned" if self.pruned else "kept"
        suffix = f" ({self.reason})" if self.reason else ""
        return f"{self.key}={self.value!r} [{tag}{suffix}]"


@dataclass
class PruneReport:
    entries: List[PruneEntry] = field(default_factory=list)

    def add(self, entry: PruneEntry) -> None:
        self.entries.append(entry)

    @property
    def pruned_count(self) -> int:
        return sum(1 for e in self.entries if e.pruned)

    @property
    def kept_count(self) -> int:
        return sum(1 for e in self.entries if not e.pruned)

    @property
    def is_clean(self) -> bool:
        return self.pruned_count == 0

    @property
    def pruned_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries if not e.pruned}

    def summary(self) -> str:
        return f"{self.pruned_count} key(s) pruned, {self.kept_count} kept."


def prune_env(
    env: Dict[str, str],
    patterns: Optional[List[str]] = None,
    remove_empty: bool = False,
) -> PruneReport:
    """Prune keys from *env* that match any glob *pattern* or are empty.

    Args:
        env: source environment dict.
        patterns: list of glob patterns (e.g. ``["LEGACY_*", "TMP_*"]``).
        remove_empty: if True, also prune keys with empty/whitespace values.

    Returns:
        A :class:`PruneReport` describing each key's fate.
    """
    patterns = patterns or []
    report = PruneReport()

    for key, value in sorted(env.items()):
        matched_pattern: Optional[str] = None
        for pat in patterns:
            if fnmatch(key, pat):
                matched_pattern = pat
                break

        if matched_pattern is not None:
            report.add(PruneEntry(key, value, pruned=True, reason=f"matches '{matched_pattern}'"))
        elif remove_empty and not value.strip():
            report.add(PruneEntry(key, value, pruned=True, reason="empty value"))
        else:
            report.add(PruneEntry(key, value, pruned=False))

    return report
