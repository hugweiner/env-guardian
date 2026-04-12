"""CLI sub-command: sanitize."""

from __future__ import annotations

import sys

import click

from env_guardian.parser import parse_env_file
from env_guardian.sanitizer import sanitize_env
from env_guardian.sanitize_formatter import format_text, format_json, format_csv


@click.command("sanitize")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--no-strip-control",
    is_flag=True,
    default=False,
    help="Disable stripping of control characters.",
)
@click.option(
    "--no-strip-null",
    is_flag=True,
    default=False,
    help="Disable stripping of null bytes.",
)
@click.option(
    "--fail-on-dirty",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any values were sanitized.",
)
def sanitize_cmd(
    env_file: str,
    fmt: str,
    no_strip_control: bool,
    no_strip_null: bool,
    fail_on_dirty: bool,
) -> None:
    """Sanitize unsafe characters from values in ENV_FILE."""
    env = parse_env_file(env_file)
    report = sanitize_env(
        env,
        strip_control=not no_strip_control,
        strip_null=not no_strip_null,
    )

    if fmt == "json":
        click.echo(format_json(report))
    elif fmt == "csv":
        click.echo(format_csv(report))
    else:
        click.echo(format_text(report))

    if fail_on_dirty and not report.is_clean():
        sys.exit(1)
