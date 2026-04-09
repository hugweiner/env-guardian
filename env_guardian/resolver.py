"""Resolve environment variable values using override layers."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ResolveEntry:
    key: str
    value: str
    source: str  # which layer provided the final value
    overridden_by: Optional[str] = None  # layer name that won over others

    def __str__(self) -> str:
        if self.overridden_by:
            return f"{self.key}={self.value} (from '{self.source}', overrode earlier layers)"
        return f"{self.key}={self.value} (from '{self.source}')"


@dataclass
class ResolveReport:
    entries: List[ResolveEntry] = field(default_factory=list)
    layers: List[str] = field(default_factory=list)

    def resolved_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def overridden_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.overridden_by]

    def summary(self) -> str:
        total = len(self.entries)
        overridden = len(self.overridden_keys())
        layer_list = ", ".join(self.layers)
        return (
            f"Resolved {total} key(s) across {len(self.layers)} layer(s) "
            f"[{layer_list}]; {overridden} key(s) overridden."
        )


def resolve_layers(
    layers: List[Tuple[str, Dict[str, str]]],
    base: Optional[Dict[str, str]] = None,
) -> ResolveReport:
    """Resolve env vars by applying named layers in order (last wins).

    Args:
        layers: List of (layer_name, env_dict) tuples applied in order.
        base: Optional base environment to start from.
    """
    report = ResolveReport(layers=[name for name, _ in layers])
    merged: Dict[str, Tuple[str, str]] = {}  # key -> (value, source)

    if base:
        for k, v in base.items():
            merged[k] = (v, "base")

    for layer_name, env in layers:
        for key, value in env.items():
            if key in merged:
                merged[key] = (value, layer_name)
            else:
                merged[key] = (value, layer_name)

    # Determine which keys were overridden (appeared in more than one layer)
    seen: Dict[str, List[str]] = {}
    if base:
        for k in base:
            seen.setdefault(k, []).append("base")
    for layer_name, env in layers:
        for k in env:
            seen.setdefault(k, []).append(layer_name)

    for key, (value, source) in sorted(merged.items()):
        overridden_by = source if len(seen.get(key, [])) > 1 else None
        report.entries.append(
            ResolveEntry(key=key, value=value, source=source, overridden_by=overridden_by)
        )

    return report
