"""Type-casting module: infer and cast env var values to Python types."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class CastEntry:
    key: str
    raw_value: str
    cast_value: Any
    inferred_type: str

    def __str__(self) -> str:
        return f"{self.key}: {self.raw_value!r} -> {self.cast_value!r} ({self.inferred_type})"


@dataclass
class CastReport:
    entries: List[CastEntry] = field(default_factory=list)

    def by_type(self, type_name: str) -> List[CastEntry]:
        return [e for e in self.entries if e.inferred_type == type_name]

    def type_names(self) -> List[str]:
        return sorted({e.inferred_type for e in self.entries})

    def as_dict(self) -> Dict[str, Any]:
        return {e.key: e.cast_value for e in self.entries}

    def summary(self) -> str:
        counts: Dict[str, int] = {}
        for e in self.entries:
            counts[e.inferred_type] = counts.get(e.inferred_type, 0) + 1
        parts = ", ".join(f"{t}: {c}" for t, c in sorted(counts.items()))
        return f"{len(self.entries)} keys cast ({parts})"


def _infer_and_cast(value: str):
    """Return (cast_value, type_name) for a raw string value."""
    if value.lower() in ("true", "false"):
        return value.lower() == "true", "bool"
    try:
        int_val = int(value)
        return int_val, "int"
    except ValueError:
        pass
    try:
        float_val = float(value)
        return float_val, "float"
    except ValueError:
        pass
    if "," in value:
        return [v.strip() for v in value.split(",")], "list"
    return value, "str"


def cast_env(env: Dict[str, str]) -> CastReport:
    """Infer and cast all values in *env*, returning a CastReport."""
    report = CastReport()
    for key, raw in env.items():
        cast_value, inferred_type = _infer_and_cast(raw)
        report.entries.append(
            CastEntry(
                key=key,
                raw_value=raw,
                cast_value=cast_value,
                inferred_type=inferred_type,
            )
        )
    return report
