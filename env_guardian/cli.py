"""CLI entry-point for env-guardian using Click."""

import sys
from pathlib import Path

import click

from env_guardian.parser import parse_env_file
from env_guardian.comparator import compare_envs


@click.group()
@click.version_option(package_name="env-guardian")
def cli() -> None:
    """env-guardian: validate and sync environment variables."""


@cli.command("compare")
@click.argument("source", type=click.Path(exists=True, dir_okay=False))
@click.argument("target", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--ignore-values",
    is_flag=True,
    default=False,
    help="Only check for key presence, skip value comparison.",
)
@click.option(
    "--ignore-key",
    "ignore_keys",
    multiple=True,
    metavar="KEY",
    help="Key(s) to exclude from comparison (repeatable).",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Exit with code 1 if any difference is found.",
)
def compare_cmd(
    source: str,
    target: str,
    ignore_values: bool,
    ignore_keys: tuple,
    strict: bool,
) -> None:
    """Compare SOURCE env file against TARGET env file."""
    try:
        src_vars = parse_env_file(source)
        tgt_vars = parse_env_file(target)
    except FileNotFoundError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(2)

    diff = compare_envs(
        src_vars,
        tgt_vars,
        ignore_values=ignore_values,
        ignore_keys=set(ignore_keys),
    )

    click.echo(diff.summary())

    if strict and not diff.is_clean:
        sys.exit(1)


if __name__ == "__main__":
    cli()
