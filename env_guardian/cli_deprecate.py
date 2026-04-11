"""CLI command: ``env-guardian deprecate`` — report deprecated env keys."""
from __future__ import annotations

import sys

import click

from env_guardian.deprecation_formatter import format_csv, format_json, format_text
from env_guardian.deprecator import deprecate_env
from env_guardian.parser import parse_env_file


@click.command("deprecate")
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
    "--fail-on-deprecated",
    is_flag=True,
    default=False,
    help="Exit with code 1 if deprecated keys are found.",
)
def deprecate_cmd(env_file: str, output_format: str, fail_on_deprecated: bool) -> None:
    """Check ENV_FILE for deprecated environment variable keys."""
    env = parse_env_file(env_file)
    report = deprecate_env(env)

    if output_format == "json":
        output = format_json(report)
    elif output_format == "csv":
        output = format_csv(report)
    else:
        output = format_text(report)

    click.echo(output)

    if fail_on_deprecated and not report.is_clean():
        sys.exit(1)
