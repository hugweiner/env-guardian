"""Substitute placeholder tokens in env values with provided replacements."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re

_PLACEHOLDER_RE = re.compile(r"\{\{\s*([\w]+)\s*\}\}")


@dataclass
class SubstituteWarning:
    key: str
    placeholder: str
    reason: str

    def __str__(self) -> str:
        return f"[{self.key}] placeholder '{{{{{self.placeholder}}}}}': {self.reason}"


@dataclass
class SubstituteReport:
    env: Dict[str, str] = field(default_factory=dict)
    warnings: List[SubstituteWarning] = field(default_factory=list)

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self) -> str:
        if self.is_clean():
            return "No unresolved placeholders."
        return f"{len(self.warnings)} unresolved placeholder(s) found."

    def substituted_count(self) -> int:
        """Return number of keys where at least one substitution was made."""
        return sum(
            1 for w in self.warnings
            if w.reason == "resolved"
        )


def substitute_env(
    env: Dict[str, str],
    replacements: Dict[str, str],
    keep_unresolved: bool = True,
) -> SubstituteReport:
    """Replace {{TOKEN}} placeholders in env values using *replacements* dict.

    Args:
        env: Source environment variables.
        replacements: Mapping of token names to replacement values.
        keep_unresolved: If True, leave unresolved placeholders intact;
                         if False, replace them with an empty string.
    Returns:
        SubstituteReport with the resulting env and any warnings.
    """
    report = SubstituteReport()

    for key, value in env.items():
        placeholders = _PLACEHOLDER_RE.findall(value)
        new_value = value

        for token in placeholders:
            if token in replacements:
                new_value = new_value.replace(f"{{{{{token}}}}}", replacements[token])
            else:
                report.warnings.append(
                    SubstituteWarning(
                        key=key,
                        placeholder=token,
                        reason="no replacement provided",
                    )
                )
                if not keep_unresolved:
                    new_value = new_value.replace(f"{{{{{token}}}}}", "")

        report.env[key] = new_value

    return report
