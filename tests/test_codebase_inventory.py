"""Tests for the repository-owned codebase inventory generator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATOR = ROOT / "scripts" / "codebase_inventory.py"


def run_generator(root: Path) -> Path:
    subprocess.run(
        [sys.executable, str(GENERATOR), "--source-root", str(root)],
        check=True,
        capture_output=True,
    )
    return root / "pipeline_output" / "codebase_inventory.jsonl"


def test_generator_is_reproducible_across_mtime_changes(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    (root / "scripts").mkdir(parents=True)
    source = root / "scripts" / "task.py"
    source.write_text("def task():\n    return 1\n", encoding="utf-8")

    inventory = run_generator(root)
    first = inventory.read_bytes()
    source.touch()
    run_generator(root)

    assert inventory.read_bytes() == first
    record = json.loads(first)
    assert record["path"] == "scripts/task.py"
    assert "mtime" not in record


def test_repository_config_selects_scan_roots(tmp_path: Path) -> None:
    root = tmp_path / "configured"
    (root / "reports" / "scripts").mkdir(parents=True)
    (root / "scripts").mkdir()
    (root / "reports" / "scripts" / "included.py").write_text(
        "VALUE = 1\n", encoding="utf-8"
    )
    (root / "scripts" / "ignored.py").write_text("VALUE = 2\n", encoding="utf-8")
    (root / ".codebase-inventory").write_text(
        "reports/scripts\n", encoding="utf-8"
    )

    records = [json.loads(line) for line in run_generator(root).read_text().splitlines()]

    assert [record["path"] for record in records] == [
        "reports/scripts/included.py"
    ]
