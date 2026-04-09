"""Generate and render .env template files from env dicts."""

from typing import Optional


DEFAULT_PLACEHOLDER = "<REQUIRED>"


def generate_template(
    env: dict[str, str],
    required_keys: Optional[list[str]] = None,
    placeholder: str = DEFAULT_PLACEHOLDER,
    include_values: bool = False,
) -> str:
    """Generate a .env template string from an existing env dict.

    Args:
        env: Source environment variables.
        required_keys: Keys that should be marked as required (empty placeholder).
        placeholder: Placeholder string for required or blanked-out keys.
        include_values: If True, retain existing values instead of blanking them.

    Returns:
        A string representing the .env template.
    """
    required = set(required_keys or [])
    lines = []
    for key in sorted(env):
        if key in required:
            lines.append(f"{key}={placeholder}")
        elif include_values:
            lines.append(f"{key}={env[key]}")
        else:
            lines.append(f"{key}=")
    return "\n".join(lines) + "\n" if lines else ""


def render_template(
    template: str,
    values: dict[str, str],
    strict: bool = False,
) -> tuple[str, list[str]]:
    """Fill a .env template string with provided values.

    Args:
        template: Template content (lines of KEY=<REQUIRED> or KEY=).
        values: Values to substitute into the template.
        strict: If True, raise ValueError when a required placeholder is unfilled.

    Returns:
        Tuple of (rendered string, list of unfilled keys).
    """
    output_lines = []
    unfilled: list[str] = []

    for line in template.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            output_lines.append(line)
            continue

        if "=" not in stripped:
            output_lines.append(line)
            continue

        key, _, current_value = stripped.partition("=")
        key = key.strip()

        if key in values:
            output_lines.append(f"{key}={values[key]}")
        elif current_value == DEFAULT_PLACEHOLDER:
            unfilled.append(key)
            output_lines.append(line)
        else:
            output_lines.append(line)

    if strict and unfilled:
        raise ValueError(f"Unfilled required keys: {', '.join(unfilled)}")

    return "\n".join(output_lines) + "\n", unfilled
