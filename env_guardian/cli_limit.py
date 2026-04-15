"""CLI command: limit — enforce value length constraints."""
from __future__ import annotations
import sys
import click

from env_guardian.parser import parse_env_file
from env_guardian.limiter import limit_env
from env_guardian.limit_formatter import format_text, format_json, format_csv


@click.command("limit")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--min", "min_length", type=int, default=None, help="Minimum value length.")
@click.option("--max", "max_length", type=int, default=None, help="Maximum value length.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any violations found.",
)
def limit_cmd(
    env_file: str,
    min_length: int | None,
    max_length: int | None,
    fmt: str,
    strict: bool,
) -> None:
    """Validate that env values satisfy min/max length constraints."""
    env = parse_env_file(env_file)
    report = limit_env(env, min_length=min_length, max_length=max_length)

    if fmt == "json":
        click.echo(format_json(report))
    elif fmt == "csv":
        click.echo(format_csv(report))
    else:
        click.echo(format_text(report))

    if strict and not report.is_clean():
        sys.exit(1)
