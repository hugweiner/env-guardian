"""Parser for .env files — reads and normalizes key-value pairs."""

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_RE = re.compile(
    r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$"
)
COMMENT_RE = re.compile(r"^\s*#")


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    for quote in ('"', "'"):
        if value.startswith(quote) and value.endswith(quote) and len(value) >= 2:
            return value[1:-1]
    return value


def parse_env_file(path: str | Path) -> Dict[str, str]:
    """
    Parse a .env file and return a dict of key-value pairs.

    Skips blank lines and comment lines (starting with #).
    Strips optional surrounding quotes from values.

    Args:
        path: Path to the .env file.

    Returns:
        Dictionary of environment variable names to their string values.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"Env file not found: {env_path}")

    result: Dict[str, str] = {}

    with env_path.open("r", encoding="utf-8") as fh:
        for lineno, raw_line in enumerate(fh, start=1):
            line = raw_line.rstrip("\n")

            # Skip blanks and comments
            if not line.strip() or COMMENT_RE.match(line):
                continue

            match = ENV_LINE_RE.match(line)
            if match:
                key = match.group("key")
                value = _strip_quotes(match.group("value").strip())
                result[key] = value

    return result


def parse_env_string(content: str) -> Dict[str, str]:
    """Parse env content from a string (useful for testing)."""
    result: Dict[str, str] = {}
    for line in content.splitlines():
        if not line.strip() or COMMENT_RE.match(line):
            continue
        match = ENV_LINE_RE.match(line)
        if match:
            key = match.group("key")
            value = _strip_quotes(match.group("value").strip())
            result[key] = value
    return result
