"""CLI entry point for env-guardian."""

import click
from env_guardian.parser import parse_env_file
from env_guardian.comparator import compare_envs
from env_guardian.validator import validate_env


@click.group()
def cli():
    """env-guardian: validate and sync environment variables."""


@cli.command(name="compare")
@click.argument("base_file", type=click.Path(exists=True))
@click.argument("target_file", type=click.Path(exists=True))
@click.option("--ignore-values", is_flag=True, default=False, help="Only compare keys, not values.")
def compare_cmd(base_file: str, target_file: str, ignore_values: bool):
    """Compare two .env files and report differences."""
    base_env = parse_env_file(base_file)
    target_env = parse_env_file(target_file)
    diff = compare_envs(base_env, target_env, ignore_values=ignore_values)
    click.echo(diff.summary())
    if not diff.is_clean:
        raise SystemExit(1)


@cli.command(name="validate")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--require",
    multiple=True,
    metavar="KEY",
    help="Key that must be present. Repeatable.",
)
@click.option(
    "--non-empty",
    multiple=True,
    metavar="KEY",
    help="Key whose value must not be empty. Repeatable.",
)
@click.option(
    "--pattern",
    multiple=True,
    metavar="KEY=REGEX",
    help="Key=regex pattern the value must satisfy. Repeatable.",
)
def validate_cmd(env_file: str, require: tuple, non_empty: tuple, pattern: tuple):
    """Validate an .env file against specified rules."""
    env = parse_env_file(env_file)

    pattern_rules = {}
    for entry in pattern:
        if "=" not in entry:
            raise click.BadParameter(f"Pattern rule must be KEY=REGEX, got: {entry}")
        key, regex = entry.split("=", 1)
        pattern_rules[key] = regex

    result = validate_env(
        env,
        required_keys=list(require) or None,
        non_empty_keys=list(non_empty) or None,
        pattern_rules=pattern_rules or None,
    )

    click.echo(result.summary())
    if not result.is_valid:
        raise SystemExit(1)
