"""Interpolate variable references within an env dictionary."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_REF_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationWarning:
    key: str
    ref: str
    message: str

    def __str__(self) -> str:
        return f"[{self.key}] references '${self.ref}': {self.message}"


@dataclass
class InterpolationResult:
    env: Dict[str, str] = field(default_factory=dict)
    warnings: List[InterpolationWarning] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean:
            return "Interpolation complete — no unresolved references."
        lines = [f"Interpolation finished with {len(self.warnings)} warning(s):"]
        for w in self.warnings:
            lines.append(f"  {w}")
        return "\n".join(lines)


def _resolve_value(
    key: str,
    value: str,
    env: Dict[str, str],
    warnings: List[InterpolationWarning],
    max_depth: int = 10,
    _depth: int = 0,
) -> str:
    if _depth > max_depth:
        warnings.append(InterpolationWarning(key, "?", "Max interpolation depth exceeded"))
        return value

    def replacer(match: re.Match) -> str:
        ref = match.group(1) or match.group(2)
        if ref in env:
            resolved = _resolve_value(key, env[ref], env, warnings, max_depth, _depth + 1)
            return resolved
        warnings.append(InterpolationWarning(key, ref, "undefined reference"))
        return match.group(0)

    return _REF_RE.sub(replacer, value)


def interpolate(env: Dict[str, str]) -> InterpolationResult:
    """Return a new env dict with $VAR / ${VAR} references expanded."""
    warnings: List[InterpolationWarning] = []
    resolved: Dict[str, str] = {}
    for key, value in env.items():
        resolved[key] = _resolve_value(key, value, env, warnings)
    return InterpolationResult(env=resolved, warnings=warnings)
