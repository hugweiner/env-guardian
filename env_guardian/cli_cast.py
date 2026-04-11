"""CLI command for casting env var values to inferred Python types."""
from __future__ import annotations

import click

from env_guardian.caster import cast_env
from env_guardian.cast_formatter import format_csv, format_json, format_text
from env_guardian.parser import parse_env_file


@click.command("cast")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--type-filter",
    default=None,
    help="Show only entries of this inferred type (bool, int, float, list, str).",
)
def cast_cmd(env_file: str, output_format: str, type_filter: str | None) -> None:
    """Infer and cast types for all values in ENV_FILE."""
    env = parse_env_file(env_file)
    report = cast_env(env)

    if type_filter:
        from env_guardian.caster import CastReport

        filtered = CastReport(entries=report.by_type(type_filter))
        report = filtered

    if output_format == "json":
        click.echo(format_json(report))
    elif output_format == "csv":
        click.echo(format_csv(report))
    else:
        click.echo(format_text(report))
