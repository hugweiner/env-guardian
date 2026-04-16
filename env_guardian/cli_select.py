"""CLI command: env-guardian select."""
from __future__ import annotations
import sys
import click

from env_guardian.parser import parse_env_file
from env_guardian.selector import select_env
from env_guardian.select_formatter import format_text, format_json, format_csv


@click.command("select")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--key", "keys", multiple=True, help="Include specific key(s).")
@click.option("--prefix", default=None, help="Include keys starting with prefix.")
@click.option("--suffix", default=None, help="Include keys ending with suffix.")
@click.option("--contains", default=None, help="Include keys containing substring.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
)
def select_cmd(
    env_file: str,
    keys: tuple,
    prefix: str | None,
    suffix: str | None,
    contains: str | None,
    fmt: str,
) -> None:
    """Select a subset of keys from ENV_FILE."""
    env = parse_env_file(env_file)
    report = select_env(
        env,
        keys=list(keys) if keys else None,
        prefix=prefix,
        suffix=suffix,
        contains=contains,
    )
    if fmt == "json":
        click.echo(format_json(report))
    elif fmt == "csv":
        click.echo(format_csv(report))
    else:
        click.echo(format_text(report))
    sys.exit(0)
