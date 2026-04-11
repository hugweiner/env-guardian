"""CLI command for filtering environment variables."""
from __future__ import annotations

import click

from env_guardian.filter_formatter import format_csv, format_json, format_text
from env_guardian.filterer import filter_env
from env_guardian.parser import parse_env_file


@click.command("filter")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--prefix", "prefixes", multiple=True, help="Include keys with this prefix (repeatable).")
@click.option("--pattern", "patterns", multiple=True, help="Include keys matching this regex (repeatable).")
@click.option("--exclude-prefix", "exclude_prefixes", multiple=True, help="Exclude keys with this prefix.")
@click.option("--exclude-pattern", "exclude_patterns", multiple=True, help="Exclude keys matching this regex.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
    help="Output format.",
)
def filter_cmd(
    env_file: str,
    prefixes: tuple,
    patterns: tuple,
    exclude_prefixes: tuple,
    exclude_patterns: tuple,
    output_format: str,
) -> None:
    """Filter keys from ENV_FILE by prefix or regex pattern."""
    env = parse_env_file(env_file)
    report = filter_env(
        env,
        prefixes=list(prefixes) or None,
        patterns=list(patterns) or None,
        exclude_prefixes=list(exclude_prefixes) or None,
        exclude_patterns=list(exclude_patterns) or None,
    )

    if output_format == "json":
        click.echo(format_json(report))
    elif output_format == "csv":
        click.echo(format_csv(report))
    else:
        click.echo(format_text(report))
