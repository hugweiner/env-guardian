"""CLI command for resolving layered environment files."""
import click

from env_guardian.parser import parse_env_file
from env_guardian.resolve_formatter import format_csv, format_json, format_text
from env_guardian.resolver import resolve_layers


@click.command("resolve")
@click.argument("files", nargs=-1, required=True, metavar="FILE...")
@click.option(
    "--labels",
    default="",
    help="Comma-separated layer names matching FILE order (e.g. base,staging,prod).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "csv"]),
    default="text",
    show_default=True,
    help="Output format.",
)
@click.option("--output", "-o", default=None, help="Write output to file instead of stdout.")
def resolve_cmd(files, labels, output_format, output):
    """Resolve env vars by merging FILE layers in order (last wins)."""
    label_list = [l.strip() for l in labels.split(",") if l.strip()]

    layers = []
    for idx, path in enumerate(files):
        try:
            env = parse_env_file(path)
        except FileNotFoundError:
            raise click.ClickException(f"File not found: {path}")
        name = label_list[idx] if idx < len(label_list) else path
        layers.append((name, env))

    report = resolve_layers(layers)

    if output_format == "json":
        result = format_json(report)
    elif output_format == "csv":
        result = format_csv(report)
    else:
        result = format_text(report)

    if output:
        with open(output, "w") as fh:
            fh.write(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)
