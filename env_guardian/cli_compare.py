"""CLI command for comparing two .env files."""
from __future__ import annotations

import sys

import click

from env_guardian.comparator import compare_envs
from env_guardian.comparator_formatter import format_csv, format_json, format_text
from env_guardian.parser import parse_env_file


@click.command("compare")
@click.argument("base_file", type=click.Path(exists=True))
@click.argument("target_file", type=click.Path(exists=True))
@click.option(
    "--ignore-values",
    is_flag=True,
    default=False,
    help="Only check for missing/extra keys; ignore value differences.",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "csv"], case_sensitive=False),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--exit-code",
    is_flag=True,
    default=False,
    help="Exit with code 1 if differences are found.",
)
def compare_cmd(
    base_file: str,
    target_file: str,
    ignore_values: bool,
    output_format: str,
    exit_code: bool,
) -> None:
    """Compare BASE_FILE against TARGET_FILE and report differences."""
    base = parse_env_file(base_file)
    target = parse_env_file(target_file)
    diff = compare_envs(base, target, ignore_values=ignore_values)

    if output_format == "json":
        click.echo(format_json(diff))
    elif output_format == "csv":
        click.echo(format_csv(diff))
    else:
        click.echo(format_text(diff))

    if exit_code and not diff.is_clean():
        sys.exit(1)
