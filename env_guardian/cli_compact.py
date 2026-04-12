"""CLI command: compact — strip empty-valued keys from an env file."""
from __future__ import annotations

import click

from env_guardian.compact_formatter import format_csv, format_json, format_text
from env_guardian.compactor import compact_env
from env_guardian.parser import parse_env_file


@click.command("compact")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--no-strip",
    is_flag=True,
    default=False,
    help="Treat whitespace-only values as non-empty.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json", "csv"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Write output to a file instead of stdout.",
)
def compact_cmd(env_file: str, no_strip: bool, fmt: str, output: str | None) -> None:
    """Remove keys with empty or whitespace-only values from ENV_FILE."""
    env = parse_env_file(env_file)
    report = compact_env(env, strip=not no_strip)

    if fmt == "json":
        rendered = format_json(report)
    elif fmt == "csv":
        rendered = format_csv(report)
    else:
        rendered = format_text(report)

    if output:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(rendered)
        click.echo(f"Report written to {output}")
    else:
        click.echo(rendered)
