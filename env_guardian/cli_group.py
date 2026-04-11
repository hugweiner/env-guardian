"""CLI command: group — display env vars organised by key prefix."""
import sys

import click

from env_guardian.group_formatter import format_csv, format_json, format_text
from env_guardian.grouper import group_env
from env_guardian.parser import parse_env_file


@click.command("group")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--separator",
    default="_",
    show_default=True,
    help="Key separator used to detect prefixes.",
)
@click.option(
    "--min-group-size",
    default=2,
    show_default=True,
    type=int,
    help="Minimum keys sharing a prefix before it becomes a group.",
)
@click.option(
    "--format",
    "output_format",
    default="text",
    type=click.Choice(["text", "json", "csv"], case_sensitive=False),
    show_default=True,
    help="Output format.",
)
def group_cmd(
    env_file: str,
    separator: str,
    min_group_size: int,
    output_format: str,
) -> None:
    """Group ENV_FILE variables by shared key prefix."""
    env = parse_env_file(env_file)
    report = group_env(env, separator=separator, min_group_size=min_group_size)

    if output_format == "json":
        click.echo(format_json(report))
    elif output_format == "csv":
        click.echo(format_csv(report))
    else:
        click.echo(format_text(report))

    if report.group_count() == 0:
        sys.exit(0)
