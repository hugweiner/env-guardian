"""CLI command for mapping environment variable keys."""

import json
import sys

import click

from env_guardian.mapper import map_env
from env_guardian.map_formatter import format_text, format_json, format_csv
from env_guardian.parser import parse_env_file


@click.command("map")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--mapping",
    required=True,
    help="JSON object mapping source keys to target keys, e.g. '{\"OLD_KEY\": \"NEW_KEY\"}'",
)
@click.option(
    "--include-unmapped",
    is_flag=True,
    default=False,
    help="Carry through keys that have no mapping entry (unchanged).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
)
def map_cmd(env_file: str, mapping: str, include_unmapped: bool, output_format: str) -> None:
    """Map environment variable keys using a JSON mapping definition."""
    try:
        key_mapping = json.loads(mapping)
    except json.JSONDecodeError as exc:
        click.echo(f"Error: invalid mapping JSON — {exc}", err=True)
        sys.exit(1)

    env = parse_env_file(env_file)
    report = map_env(env, key_mapping, skip_missing=not include_unmapped)

    if output_format == "json":
        click.echo(format_json(report))
    elif output_format == "csv":
        click.echo(format_csv(report))
    else:
        click.echo(format_text(report))
