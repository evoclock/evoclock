#!/usr/bin/env python3
"""Render a self-contained Power Station report from simple JSON metadata."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE = REPO_ROOT / "reports" / "templates" / "powerstation-report.html"


PLACEHOLDERS = {
    "REPORT_TITLE": "title",
    "BENCHMARK_NAME": "benchmark",
    "MODEL_COUNT": "model_count",
    "PROBLEM_COUNT": "problem_count",
    "RUN_SETTING": "run_setting",
    "ONE_SENTENCE_FINDING": "finding",
    "OPENING_CONTEXT": "opening_context",
    "METHOD_SUMMARY": "method_summary",
    "NARRATIVE_BRIDGE_TO_EVIDENCE": "evidence_bridge",
    "DATE": "generated_date",
    "SOURCE_DATA": "source_data",
}


def load_metadata(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return data


def render(template: str, metadata: dict[str, object]) -> str:
    rendered = template
    for placeholder, key in PLACEHOLDERS.items():
        value = metadata.get(key, placeholder)
        rendered = rendered.replace(placeholder, html.escape(str(value), quote=False))
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render reports/templates/powerstation-report.html from JSON metadata."
    )
    parser.add_argument("metadata", type=Path, help="JSON metadata file")
    parser.add_argument("output", type=Path, help="HTML output path")
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help=f"HTML template path, default: {DEFAULT_TEMPLATE}",
    )
    args = parser.parse_args()

    metadata = load_metadata(args.metadata)
    template = args.template.read_text(encoding="utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(template, metadata), encoding="utf-8")


if __name__ == "__main__":
    main()
