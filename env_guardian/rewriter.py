"""Rewrite environment variable keys and/or values using regex-based rules."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class RewriteEntry:
    key: str
    original_key: str
    value: str
    original_value: str
    key_rewritten: bool
    value_rewritten: bool

    def __str__(self) -> str:  # pragma: no cover
        parts = []
        if self.key_rewritten:
            parts.append(f"key: {self.original_key!r} -> {self.key!r}")
        if self.value_rewritten:
            parts.append(f"value: {self.original_value!r} -> {self.value!r}")
        tag = ", ".join(parts) if parts else "unchanged"
        return f"{self.key}: [{tag}]"


@dataclass
class RewriteReport:
    _entries: List[RewriteEntry] = field(default_factory=list)

    def add(self, entry: RewriteEntry) -> None:
        self._entries.append(entry)

    @property
    def entries(self) -> List[RewriteEntry]:
        return list(self._entries)

    @property
    def rewritten_count(self) -> int:
        return sum(1 for e in self._entries if e.key_rewritten or e.value_rewritten)

    @property
    def result_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self._entries}

    def is_clean(self) -> bool:
        return self.rewritten_count == 0

    def summary(self) -> str:
        total = len(self._entries)
        rw = self.rewritten_count
        return f"{rw}/{total} entries rewritten."


Rule = Tuple[str, str]  # (pattern, replacement)


def rewrite_env(
    env: Dict[str, str],
    key_rules: Optional[List[Rule]] = None,
    value_rules: Optional[List[Rule]] = None,
) -> RewriteReport:
    """Apply regex substitution rules to keys and/or values of *env*.

    Each rule is a ``(pattern, replacement)`` pair passed to :func:`re.sub`.
    Rules are applied in order; each rule operates on the result of the previous.
    """
    key_rules = key_rules or []
    value_rules = value_rules or []
    report = RewriteReport()

    for orig_key, orig_value in env.items():
        new_key = orig_key
        for pattern, replacement in key_rules:
            new_key = re.sub(pattern, replacement, new_key)

        new_value = orig_value
        for pattern, replacement in value_rules:
            new_value = re.sub(pattern, replacement, new_value)

        entry = RewriteEntry(
            key=new_key,
            original_key=orig_key,
            value=new_value,
            original_value=orig_value,
            key_rewritten=new_key != orig_key,
            value_rewritten=new_value != orig_value,
        )
        report.add(entry)

    return report
