"""CLI subcommand for auditing environment files."""

import sys
import click

from env_guardian.parser import parse_env_file, parse_env_string
from env_guardian.auditor import audit_env
from env_guardian.audit_formatter import format_text, format_json, format_csv


@click.command("audit")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
    help="Output format for the audit report.",
)
@click.option(
    "--no-weak-check",
    is_flag=True,
    default=False,
    help="Skip detection of weak/placeholder secret values.",
)
@click.option(
    "--fail-on-issues",
    is_flag=True,
    default=False,
    help="Exit with a non-zero status code if any issues are found.",
)
def audit_cmd(env_file: str, output_format: str, no_weak_check: bool, fail_on_issues: bool) -> None:
    """Audit ENV_FILE for security and quality issues."""
    try:
        env = parse_env_file(env_file)
    except (OSError, ValueError) as exc:
        click.echo(f"Error reading file: {exc}", err=True)
        sys.exit(2)

    report = audit_env(env, check_weak_values=not no_weak_check)

    formatters = {"text": format_text, "json": format_json, "csv": format_csv}
    output = formatters[output_format](report)
    click.echo(output, nl=output_format != "text")

    if fail_on_issues and not report.is_clean():
        sys.exit(1)
