from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class JoinEntry:
    key: str
    value: str
    sources: List[str]  # names of envs that contributed this key

    def __str__(self) -> str:
        return f"{self.key}={self.value} (from: {', '.join(self.sources)})"


@dataclass
class JoinReport:
    entries: List[JoinEntry] = field(default_factory=list)
    _env_cache: Dict[str, JoinEntry] = field(default_factory=dict, repr=False)

    def add(self, entry: JoinEntry) -> None:
        self.entries.append(entry)
        self._env_cache[entry.key] = entry

    def joined_count(self) -> int:
        return len(self.entries)

    def joined_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def keys_from(self, source: str) -> List[str]:
        return [e.key for e in self.entries if source in e.sources]

    def summary(self) -> str:
        return f"{self.joined_count()} keys joined"


def join_envs(
    envs: Dict[str, Dict[str, str]],
    strategy: str = "last",
) -> JoinReport:
    """Merge multiple named envs into one.

    strategy:
      'last'  – last env wins on conflict (default)
      'first' – first env wins on conflict
    """
    if strategy not in ("last", "first"):
        raise ValueError(f"Unknown strategy: {strategy!r}")

    report = JoinReport()
    merged: Dict[str, str] = {}
    key_sources: Dict[str, List[str]] = {}

    ordered = list(envs.items())
    if strategy == "first":
        ordered = list(reversed(ordered))

    for name, env in ordered:
        for key, value in env.items():
            merged[key] = value
            key_sources.setdefault(key, [])
            if name not in key_sources[key]:
                key_sources[key].append(name)

    if strategy == "first":
        for sources in key_sources.values():
            sources.reverse()

    for key, value in sorted(merged.items()):
        report.add(JoinEntry(key=key, value=value, sources=key_sources[key]))

    return report
