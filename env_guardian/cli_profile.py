"""CLI command for the profiler feature."""

import click

from env_guardian.parser import parse_env_file
from env_guardian.profiler import profile_env
from env_guardian.profile_formatter import format_text, format_json, format_csv


@click.command("profile")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Write output to file.")
def profile_cmd(env_file: str, output_format: str, output: str) -> None:
    """Profile variables in ENV_FILE by category and emptiness."""
    env = parse_env_file(env_file)
    report = profile_env(env)

    if output_format == "json":
        result = format_json(report)
    elif output_format == "csv":
        result = format_csv(report)
    else:
        result = format_text(report)

    if output:
        with open(output, "w") as fh:
            fh.write(result)
        click.echo(f"Profile written to {output}")
    else:
        click.echo(result)
