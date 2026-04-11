"""Stack multiple env layers and report precedence for each key."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StackEntry:
    key: str
    value: str
    winning_layer: str
    all_layers: Dict[str, Optional[str]] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.key}={self.value!r} (from {self.winning_layer})"


@dataclass
class StackReport:
    entries: List[StackEntry] = field(default_factory=list)
    layer_names: List[str] = field(default_factory=list)

    def by_key(self, key: str) -> Optional[StackEntry]:
        for entry in self.entries:
            if entry.key == key:
                return entry
        return None

    def overridden_count(self) -> int:
        """Keys that appear in more than one layer."""
        return sum(
            1 for e in self.entries
            if sum(1 for v in e.all_layers.values() if v is not None) > 1
        )

    def resolved_env(self) -> Dict[str, str]:
        return {e.key: e.value for e in self.entries}

    def summary(self) -> str:
        total = len(self.entries)
        overridden = self.overridden_count()
        layers = len(self.layer_names)
        return (
            f"{total} key(s) resolved across {layers} layer(s); "
            f"{overridden} key(s) overridden by a higher-priority layer"
        )


def stack_envs(
    layers: List[Dict[str, str]],
    layer_names: Optional[List[str]] = None,
) -> StackReport:
    """Resolve keys across ordered layers (last layer = highest priority)."""
    if layer_names is None:
        layer_names = [f"layer{i}" for i in range(len(layers))]

    if len(layer_names) != len(layers):
        raise ValueError("layer_names length must match layers length")

    all_keys: List[str] = []
    for layer in layers:
        for k in layer:
            if k not in all_keys:
                all_keys.append(k)

    report = StackReport(layer_names=list(layer_names))

    for key in all_keys:
        per_layer: Dict[str, Optional[str]] = {
            name: layer.get(key) for name, layer in zip(layer_names, layers)
        }
        winning_name = layer_names[0]
        winning_value = ""
        for name, layer in zip(layer_names, layers):
            if key in layer:
                winning_name = name
                winning_value = layer[key]

        report.entries.append(
            StackEntry(
                key=key,
                value=winning_value,
                winning_layer=winning_name,
                all_layers=per_layer,
            )
        )

    return report
