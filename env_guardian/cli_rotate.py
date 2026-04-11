"""CLI command: rotate — flag stale keys and emit rotation suggestions."""
from __future__ import annotations

import click

from env_guardian.parser import parse_env_file
from env_guardian.rotator import rotate_env
from env_guardian.rotate_formatter import format_csv, format_json, format_text


@click.command("rotate")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--suffix",
    default=None,
    help="Custom suffix appended to rotated key names (default: current year).",
)
@click.option(
    "--no-stale",
    "flag_stale",
    is_flag=True,
    default=True,
    help="Disable stale-suffix detection.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option(
    "--fail-on-stale",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any stale keys are found.",
)
def rotate_cmd(
    env_file: str,
    suffix: str | None,
    flag_stale: bool,
    fmt: str,
    fail_on_stale: bool,
) -> None:
    """Analyse ENV_FILE for stale keys and suggest rotated names."""
    env = parse_env_file(env_file)
    report = rotate_env(env, suffix=suffix, flag_stale=flag_stale)

    if fmt == "json":
        click.echo(format_json(report))
    elif fmt == "csv":
        click.echo(format_csv(report))
    else:
        click.echo(format_text(report))

    if fail_on_stale and not report.is_clean():
        raise SystemExit(1)
