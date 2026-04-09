"""CLI commands for env snapshot and diff."""
from __future__ import annotations

import json
import sys

import click

from env_guardian.parser import parse_env_file
from env_guardian.snapshot_formatter import format_csv, format_json, format_text
from env_guardian.snapshotter import (
    diff_snapshots,
    snapshot_from_dict,
    snapshot_to_dict,
    take_snapshot,
)


@click.group("snapshot")
def snapshot_cmd() -> None:
    """Snapshot and diff environment files over time."""


@snapshot_cmd.command("take")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--label", default="snapshot", show_default=True, help="Snapshot label.")
@click.option("--output", type=click.Path(), default=None, help="Save snapshot JSON to file.")
def take_cmd(env_file: str, label: str, output: str | None) -> None:
    """Capture a snapshot of ENV_FILE."""
    env = parse_env_file(env_file)
    snap = take_snapshot(env, label=label)
    data = json.dumps(snapshot_to_dict(snap), indent=2)

    if output:
        with open(output, "w") as fh:
            fh.write(data)
        click.echo(f"Snapshot saved to {output}")
    else:
        click.echo(data)


@snapshot_cmd.command("diff")
@click.argument("old_snapshot", type=click.Path(exists=True))
@click.argument("new_snapshot", type=click.Path(exists=True))
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
)
def diff_cmd(old_snapshot: str, new_snapshot: str, fmt: str) -> None:
    """Diff two snapshot files."""
    with open(old_snapshot) as fh:
        old = snapshot_from_dict(json.load(fh))
    with open(new_snapshot) as fh:
        new = snapshot_from_dict(json.load(fh))

    diff = diff_snapshots(old, new)

    if fmt == "json":
        click.echo(format_json(diff))
    elif fmt == "csv":
        click.echo(format_csv(diff))
    else:
        click.echo(format_text(diff, old_label=old.label, new_label=new.label))

    if not diff.is_clean():
        sys.exit(1)
