"""Aliaser: map environment variable keys to alternative names."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasEntry:
    original_key: str
    alias_key: str
    value: str
    skipped: bool = False
    skip_reason: Optional[str] = None

    def __str__(self) -> str:
        if self.skipped:
            return f"{self.original_key} -> {self.alias_key} [SKIPPED: {self.skip_reason}]"
        return f"{self.original_key} -> {self.alias_key} = {self.value}"


@dataclass
class AliasReport:
    entries: List[AliasEntry] = field(default_factory=list)

    def add(self, entry: AliasEntry) -> None:
        self.entries.append(entry)

    def aliased_count(self) -> int:
        return sum(1 for e in self.entries if not e.skipped)

    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if e.skipped)

    def result_env(self) -> Dict[str, str]:
        """Return env dict with alias keys replacing original keys."""
        return {e.alias_key: e.value for e in self.entries if not e.skipped}

    def summary(self) -> str:
        return (
            f"{self.aliased_count()} key(s) aliased, "
            f"{self.skipped_count()} skipped."
        )


def alias_env(
    env: Dict[str, str],
    alias_map: Dict[str, str],
    keep_original: bool = False,
) -> AliasReport:
    """Apply alias_map to env, renaming keys to their aliases.

    Args:
        env: Source environment dict.
        alias_map: Mapping of original_key -> alias_key.
        keep_original: If True, retain the original key alongside the alias.

    Returns:
        AliasReport describing all alias operations.
    """
    report = AliasReport()

    for original, alias in alias_map.items():
        if original not in env:
            report.add(AliasEntry(
                original_key=original,
                alias_key=alias,
                value="",
                skipped=True,
                skip_reason="key not found in env",
            ))
            continue

        report.add(AliasEntry(
            original_key=original,
            alias_key=alias,
            value=env[original],
        ))

    if keep_original:
        # Merge original keys not covered by alias map back in
        aliased_originals = {e.original_key for e in report.entries if not e.skipped}
        for key, value in env.items():
            if key not in aliased_originals:
                report.add(AliasEntry(original_key=key, alias_key=key, value=value))

    return report
