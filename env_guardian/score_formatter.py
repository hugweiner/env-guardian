"""Formatters for ScoreBreakdown output."""

import json
import csv
import io

from env_guardian.scorer import ScoreBreakdown


def format_text(breakdown: ScoreBreakdown) -> str:
    lines = [
        "=== Environment Health Score ===",
        f"  Final Score  : {breakdown.final_score} / 100",
        f"  Grade        : {breakdown.grade}",
        f"  Audit Penalty: -{breakdown.audit_penalty} pts",
        f"  Lint Penalty : -{breakdown.lint_penalty} pts",
        f"  Raw Score    : {breakdown.raw_score}",
    ]
    return "\n".join(lines)


def format_json(breakdown: ScoreBreakdown) -> str:
    data = {
        "final_score": breakdown.final_score,
        "grade": breakdown.grade,
        "audit_penalty": breakdown.audit_penalty,
        "lint_penalty": breakdown.lint_penalty,
        "raw_score": breakdown.raw_score,
    }
    return json.dumps(data, indent=2)


def format_csv(breakdown: ScoreBreakdown) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["metric", "value"])
    writer.writerow(["final_score", breakdown.final_score])
    writer.writerow(["grade", breakdown.grade])
    writer.writerow(["audit_penalty", breakdown.audit_penalty])
    writer.writerow(["lint_penalty", breakdown.lint_penalty])
    writer.writerow(["raw_score", breakdown.raw_score])
    return buf.getvalue()
