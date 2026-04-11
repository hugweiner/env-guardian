"""Format a StackReport as text, JSON, or CSV."""
from __future__ import annotations
import csv
import io
import json
from typing import List

from env_guardian.stacker import StackReport, StackEntry


def _sorted_entries(report: StackReport) -> List[StackEntry]:
    return sorted(report.entries, key=lambda e: e.key)


def format_text(report: StackReport) -> str:
    lines: List[str] = []
    lines.append("=== Env Stack Report ===")
    lines.append(f"Layers : {', '.join(report.layer_names)}")
    lines.append(report.summary())
    lines.append("")

    if not report.entries:
        lines.append("(no keys)")
        return "\n".join(lines)

    for entry in _sorted_entries(report):
        overridden = (
            sum(1 for v in entry.all_layers.values() if v is not None) > 1
        )
        flag = " [overridden]" if overridden else ""
        lines.append(f"  {entry.key}={entry.value!r}  <- {entry.winning_layer}{flag}")
        for layer_name, val in entry.all_layers.items():
            if val is not None and layer_name != entry.winning_layer:
                lines.append(f"      {layer_name}: {val!r}")

    return "\n".join(lines)


def format_json(report: StackReport) -> str:
    data = {
        "layers": report.layer_names,
        "summary": report.summary(),
        "entries": [
            {
                "key": e.key,
                "value": e.value,
                "winning_layer": e.winning_layer,
                "all_layers": e.all_layers,
            }
            for e in _sorted_entries(report)
        ],
    }
    return json.dumps(data, indent=2)


def format_csv(report: StackReport) -> str:
    buf = io.StringIO()
    fieldnames = ["key", "value", "winning_layer"] + list(report.layer_names)
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for entry in _sorted_entries(report):
        row: dict = {
            "key": entry.key,
            "value": entry.value,
            "winning_layer": entry.winning_layer,
        }
        for name in report.layer_names:
            row[name] = entry.all_layers.get(name, "")
        writer.writerow(row)
    return buf.getvalue()
