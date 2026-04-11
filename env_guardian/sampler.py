"""Sample a subset of environment variables based on various strategies."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SampleEntry:
    key: str
    value: str
    index: int  # original position in sorted key list

    def __str__(self) -> str:
        return f"{self.key}={self.value}  (index={self.index})"


@dataclass
class SampleReport:
    entries: List[SampleEntry] = field(default_factory=list)
    strategy: str = "random"
    total_keys: int = 0

    def sampled_count(self) -> int:
        return len(self.entries)

    def sampled_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def summary(self) -> str:
        return (
            f"Sampled {self.sampled_count()} of {self.total_keys} keys "
            f"using '{self.strategy}' strategy."
        )


def sample_env(
    env: Dict[str, str],
    n: int,
    strategy: str = "random",
    seed: Optional[int] = None,
    prefix: Optional[str] = None,
) -> SampleReport:
    """Return a SampleReport with *n* entries chosen from *env*.

    Strategies:
      - ``random``  – uniformly random sample (default)
      - ``first``   – first *n* keys in alphabetical order
      - ``last``    – last *n* keys in alphabetical order
      - ``prefix``  – all keys that start with *prefix* (n is ignored)
    """
    report = SampleReport(strategy=strategy, total_keys=len(env))

    sorted_keys = sorted(env.keys())

    if strategy == "prefix":
        pfx = prefix or ""
        selected = [k for k in sorted_keys if k.startswith(pfx)]
    elif strategy == "first":
        selected = sorted_keys[:n]
    elif strategy == "last":
        selected = sorted_keys[-n:] if n <= len(sorted_keys) else sorted_keys
    else:  # random
        rng = random.Random(seed)
        k = min(n, len(sorted_keys))
        selected = rng.sample(sorted_keys, k)
        selected = sorted(selected)  # stable output order

    for key in selected:
        idx = sorted_keys.index(key)
        report.entries.append(SampleEntry(key=key, value=env[key], index=idx))

    return report
