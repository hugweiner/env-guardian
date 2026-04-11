"""Sort environment variable keys with optional grouping strategies."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SortReport:
    """Result of sorting an environment variable dict."""

    sorted_env: Dict[str, str]
    original_order: List[str]
    strategy: str
    groups: Dict[str, List[str]] = field(default_factory=dict)

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def summary(self) -> str:
        count = len(self.sorted_env)
        if self.groups:
            group_count = len(self.groups)
            return (
                f"Sorted {count} key(s) using '{self.strategy}' strategy "
                f"into {group_count} group(s)."
            )
        return f"Sorted {count} key(s) using '{self.strategy}' strategy."


def _prefix_group(key: str) -> str:
    """Return the prefix group for a key (part before first underscore)."""
    return key.split("_")[0] if "_" in key else key


def sort_env(
    env: Dict[str, str],
    strategy: str = "alpha",
    reverse: bool = False,
    group_by_prefix: bool = False,
) -> SortReport:
    """Sort environment variables by the given strategy.

    Strategies:
        alpha   - alphabetical by key (default)
        length  - by key length, shortest first
        value   - alphabetical by value

    Args:
        env: Mapping of env var keys to values.
        strategy: Sorting strategy name.
        reverse: If True, reverse the sort order.
        group_by_prefix: If True, group keys by their prefix before the first
            underscore and sort within each group.

    Returns:
        SortReport with the sorted env and metadata.
    """
    valid_strategies = {"alpha", "length", "value"}
    if strategy not in valid_strategies:
        raise ValueError(
            f"Unknown strategy '{strategy}'. Choose from: {', '.join(sorted(valid_strategies))}"
        )

    original_order = list(env.keys())

    key_funcs = {
        "alpha": lambda k: k,
        "length": lambda k: (len(k), k),
        "value": lambda k: (env[k], k),
    }
    key_func = key_funcs[strategy]

    groups: Dict[str, List[str]] = {}
    if group_by_prefix:
        for k in env:
            prefix = _prefix_group(k)
            groups.setdefault(prefix, []).append(k)
        sorted_keys: List[str] = []
        for prefix in sorted(groups.keys(), reverse=reverse):
            groups[prefix] = sorted(groups[prefix], key=key_func, reverse=reverse)
            sorted_keys.extend(groups[prefix])
    else:
        sorted_keys = sorted(env.keys(), key=key_func, reverse=reverse)

    sorted_env = {k: env[k] for k in sorted_keys}
    return SortReport(
        sorted_env=sorted_env,
        original_order=original_order,
        strategy=strategy,
        groups=groups,
    )
