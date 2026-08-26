#!/usr/bin/env python3
"""Score Judgment Loop observations without hiding routing failure classes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ACTIVATIONS = {"none", "light", "full"}
UPDATES = {"not_applicable", "change", "hold", "strengthen_stop"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{number}: invalid JSON: {exc}") from exc
    return rows


def score(cases, observations):
    case_by_id = {case["id"]: case for case in cases}
    observed_by_id = {row["case_id"]: row for row in observations}
    unknown = sorted(set(observed_by_id) - set(case_by_id))
    if unknown:
        raise SystemExit(f"Unknown case_id values: {', '.join(unknown)}")

    summary = {
        "cases_total": len(cases),
        "cases_observed": len(observed_by_id),
        "missing_cases": [],
        "false_positive_activations": [],
        "false_negatives": [],
        "activation_mismatches": [],
        "evidence_update_errors": [],
        "correct_evidence_updates": [],
    }

    for case in cases:
        case_id = case["id"]
        row = observed_by_id.get(case_id)
        if row is None:
            summary["missing_cases"].append(case_id)
            continue

        observed_activation = row.get("observed_activation")
        if observed_activation not in ACTIVATIONS:
            raise SystemExit(
                f"{case_id}: observed_activation must be one of {sorted(ACTIVATIONS)}"
            )
        expected_activation = case["expected_activation"]

        if expected_activation == "none" and observed_activation != "none":
            summary["false_positive_activations"].append(case_id)
        elif expected_activation == "full" and observed_activation == "none":
            summary["false_negatives"].append(case_id)
        elif expected_activation != observed_activation:
            summary["activation_mismatches"].append(case_id)

        if case["class"] == "evidence_update":
            observed_update = row.get("observed_update")
            if observed_update not in UPDATES:
                raise SystemExit(
                    f"{case_id}: observed_update must be one of {sorted(UPDATES)}"
                )
            if observed_update == case["expected_update"]:
                summary["correct_evidence_updates"].append(case_id)
            else:
                summary["evidence_update_errors"].append(case_id)

    return summary


def render_markdown(summary):
    def line(label, key):
        values = summary[key]
        detail = ", ".join(values) if values else "none"
        return f"- **{label}:** {len(values)} — {detail}"

    return "\n".join(
        [
            "# Judgment Loop evaluation scorecard",
            "",
            f"- **Observed:** {summary['cases_observed']} / {summary['cases_total']}",
            line("False-positive activations", "false_positive_activations"),
            line("False negatives", "false_negatives"),
            line("Other activation mismatches", "activation_mismatches"),
            line("Evidence-update errors", "evidence_update_errors"),
            line("Correct evidence updates", "correct_evidence_updates"),
            line("Missing cases", "missing_cases"),
        ]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=Path("evals/cases.json"))
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()

    summary = score(load_json(args.cases), load_jsonl(args.results))
    if args.format == "json":
        print(json.dumps(summary, indent=2))
    else:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
