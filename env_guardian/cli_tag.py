"""CLI command for tagging environment variables."""

import json
import sys

import click

from env_guardian.parser import parse_env_file
from env_guardian.tag_formatter import format_csv, format_json, format_text
from env_guardian.tagger import tag_env


@click.command("tag")
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
    "--extra-rules",
    default=None,
    help='JSON string mapping tag names to pattern lists, e.g. \'{"infra":["PORT"]}\'\'.',
)
@click.option(
    "--manual-tags",
    default=None,
    help='JSON string mapping key names to tag lists, e.g. \'{"MY_KEY":["custom"]}\'\'.',
)
def tag_cmd(
    env_file: str,
    output_format: str,
    extra_rules: str,
    manual_tags: str,
) -> None:
    """Tag environment variables in ENV_FILE using built-in and custom rules."""
    env = parse_env_file(env_file)

    extra = None
    if extra_rules:
        try:
            extra = json.loads(extra_rules)
        except json.JSONDecodeError as exc:
            click.echo(f"Error: --extra-rules is not valid JSON: {exc}", err=True)
            sys.exit(1)

    manual = None
    if manual_tags:
        try:
            manual = json.loads(manual_tags)
        except json.JSONDecodeError as exc:
            click.echo(f"Error: --manual-tags is not valid JSON: {exc}", err=True)
            sys.exit(1)

    report = tag_env(env, extra_rules=extra, manual_tags=manual)

    if output_format == "json":
        click.echo(format_json(report))
    elif output_format == "csv":
        click.echo(format_csv(report))
    else:
        click.echo(format_text(report))
