#!/usr/bin/env python
"""Walk a repo and emit a structured inventory of its code.

For each Python file under the scanned directories: module docstring, top-level
imports, top-level constants/assignments, function and class signatures (with
their docstrings) — all extracted via ast, no execution. For each shell file:
header comments, function names, uppercase variable assignments — via regex.
Extensionless files whose first line is a python/bash shebang are covered too,
so a main script with no extension is not invisible to prior-art lookups.

Each record carries cheap signals up front: blob_sha (== git hash-object, so a
record is checkable against a commit), loc, and per function/class
loc, complexity, public, and refcount (in-repo references minus the definition —
a single-use function is a smell). Short scalar fields come first and the long
fields (docstrings, imports, signatures) last, so a record line scans easily.

Purpose: give an agent or a developer a cheap lookup of "what already exists in
this repo" before writing new code. One JSONL record per file.

Defaults:
    --source-root  : cwd
    --include-dirs : scripts workflows src
    --output       : <source-root>/pipeline_output/codebase_inventory.jsonl

Missing include-dirs are skipped silently. Output directory is created if
absent. Hidden dirs and __pycache__ are always skipped.

Usage:
    python scripts/codebase_inventory.py
    python scripts/codebase_inventory.py --include-dirs scripts tests
    python scripts/codebase_inventory.py --source-root /path/to/repo
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

SHELL_FUNC_RE = re.compile(
    r"^\s*(?:function\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{", re.MULTILINE
)
SHELL_VAR_RE = re.compile(
    r"^\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)=([^\n]{1,120})", re.MULTILINE
)
IDENT_RE = re.compile(r"\b\w+\b")

DEFAULT_INCLUDE_DIRS = ["scripts", "workflows", "src"]
CONFIG_FILE = ".codebase-inventory"


def configured_include_dirs(source_root: Path) -> list[str]:
    """Read repository-owned scan roots, or use the portable defaults."""
    config = source_root / CONFIG_FILE
    if not config.is_file():
        return DEFAULT_INCLUDE_DIRS
    values = [
        line.strip()
        for line in config.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    return values or DEFAULT_INCLUDE_DIRS


def _git_blob_sha(data: bytes) -> str:
    """The git blob sha of file bytes (== git hash-object), computed in-process so a
    record can be checked against `git rev-parse <commit>:<path>` for drift."""
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def _shebang_kind(path: Path) -> str | None:
    """For an extensionless file: 'python' or 'shell' inferred from its #! line, else
    None. This is what makes an extensionless main script visible to the inventory."""
    try:
        first = path.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
    except Exception:
        return None
    if not first.startswith("#!"):
        return None
    if "python" in first:
        return "python"
    if "bash" in first or "/sh" in first or "env sh" in first:
        return "shell"
    return None


def _complexity(node: ast.AST) -> int:
    """Cyclomatic complexity: 1 plus the branch points within the node. A simple
    branch count, deliberately not a full control-flow analysis (anti-bloat)."""
    score = 1
    for child in ast.walk(node):
        if isinstance(
            child,
            (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.ExceptHandler,
                ast.With,
                ast.AsyncWith,
                ast.Assert,
            ),
        ):
            score += 1
        elif isinstance(child, ast.BoolOp):
            score += len(child.values) - 1
        elif isinstance(child, ast.IfExp):
            score += 1
        elif isinstance(child, ast.comprehension):
            score += 1 + len(child.ifs)
        elif isinstance(child, ast.Match):
            score += len(child.cases)
    return score


def _loc(node: ast.AST) -> int | None:
    end = getattr(node, "end_lineno", None)
    start = getattr(node, "lineno", None)
    return (end - start + 1) if (end and start) else None


def extract_python(path: Path) -> dict[str, Any]:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": f"read_error: {e}"}
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        return {"error": f"syntax_error: {e}"}

    module_doc = ast.get_docstring(tree)
    imports: list[str] = []
    constants: list[dict[str, str]] = []
    functions: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                imports.append(f"{mod}.{alias.name}" if mod else alias.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        value_repr = _summarize_value(node.value)
                    except Exception:
                        value_repr = "<unparsed>"
                    constants.append({"name": target.id, "value": value_repr[:200]})
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            try:
                value_repr = (
                    _summarize_value(node.value)
                    if node.value is not None
                    else "<annotated>"
                )
            except Exception:
                value_repr = "<unparsed>"
            constants.append({"name": node.target.id, "value": value_repr[:200]})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(_extract_function(node))
        elif isinstance(node, ast.ClassDef):
            methods = []
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(_extract_function(child))
            classes.append(
                {
                    "name": node.name,
                    "loc": _loc(node),
                    "public": not node.name.startswith("_"),
                    "refcount": None,  # filled in main() pass 2 from the global identifier freq
                    "bases": [_name_of(b) for b in node.bases],
                    "methods": methods,
                    "docstring": ast.get_docstring(node),
                }
            )

    return {
        "language": "python",
        "imports": imports[:50],
        "constants": constants[:50],
        "functions": functions,
        "classes": classes,
        "module_docstring": module_doc,
    }


def _extract_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    args = []
    for a in node.args.args:
        anno = ast.unparse(a.annotation) if a.annotation else None
        args.append({"name": a.arg, "annotation": anno})
    return {
        "name": node.name,
        "loc": _loc(node),
        "complexity": _complexity(node),
        "public": not node.name.startswith("_"),
        "refcount": None,  # filled in main() pass 2 from the global identifier freq
        "args": args,
        "returns": ast.unparse(node.returns) if node.returns else None,
        "decorators": [ast.unparse(d) for d in node.decorator_list][:5],
        "docstring": ast.get_docstring(node),
    }


def _name_of(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return "<unparsed>"


def _summarize_value(node: ast.AST) -> str:
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return f"<{type(node).__name__.lower()} len={len(node.elts)}>"
    if isinstance(node, ast.Dict):
        return f"<dict len={len(node.keys)}>"
    if isinstance(node, ast.Call):
        return f"<call {_name_of(node.func)}(...)>"
    return _name_of(node)


def extract_shell(path: Path) -> dict[str, Any]:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": f"read_error: {e}"}
    header_lines: list[str] = []
    for line in src.splitlines()[:20]:
        s = line.strip()
        if s.startswith("#") and not s.startswith("#!/"):
            header_lines.append(s.lstrip("#").strip())
    funcs = [{"name": m.group(1)} for m in SHELL_FUNC_RE.finditer(src)]
    vars_ = [
        {"name": m.group(1), "value": m.group(2).strip()}
        for m in SHELL_VAR_RE.finditer(src)
    ]
    return {
        "language": "shell",
        "functions": funcs,
        "variables": vars_[:50],
        "header_comments": "\n".join(header_lines) or None,
    }


def _kind_of(path: Path) -> str | None:
    """Which extractor (if any) handles this file: by suffix, or by shebang when the
    file is extensionless."""
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "python"
    if suffix == ".sh":
        return "shell"
    if suffix == "":
        return _shebang_kind(path)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root to walk (default: cwd).",
    )
    parser.add_argument(
        "--include-dirs",
        nargs="+",
        default=None,
        help=(
            "Subdirs under source-root to walk. The default comes from "
            f"{CONFIG_FILE}, then falls back to {' '.join(DEFAULT_INCLUDE_DIRS)}."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSONL path (default: <source-root>/pipeline_output/codebase_inventory.jsonl).",
    )
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    include_dirs = args.include_dirs or configured_include_dirs(source_root)
    output = args.output or (
        source_root / "pipeline_output" / "codebase_inventory.jsonl"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    roots = [source_root / d for d in include_dirs]
    missing = [r for r in roots if not r.is_dir()]
    present = [r for r in roots if r.is_dir()]
    for r in missing:
        print(f"skip missing dir: {r.relative_to(source_root)}", file=sys.stderr)

    # Repositories without recognized code roots still receive a valid empty
    # inventory. This keeps the cross-repository contract universal while the
    # repository-local config remains authoritative for what counts as code.

    # Pass 1: build records and accumulate a global identifier frequency for refcounts.
    records: list[dict[str, Any]] = []
    freq: Counter[str] = Counter()
    by_lang: dict[str, int] = {}
    for root in present:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel_to_root = path.relative_to(root)
            if any(
                part.startswith(".") or part == "__pycache__"
                for part in rel_to_root.parts
            ):
                continue
            kind = _kind_of(path)
            if kind is None:
                continue
            data = extract_python(path) if kind == "python" else extract_shell(path)
            try:
                raw = path.read_bytes()
            except Exception:
                continue
            text = raw.decode("utf-8", errors="replace")
            freq.update(IDENT_RE.findall(text))
            rel = path.relative_to(source_root)
            parts = rel.parts
            subdir = parts[1] if len(parts) >= 3 else parts[0]
            record = {
                "path": str(rel),
                "subdir": subdir,
                "filename": path.name,
                "blob_sha": _git_blob_sha(raw),
                "loc": len(text.splitlines()),
                "size_bytes": len(raw),
                **data,
            }
            records.append(record)
            lang = data.get("language", "error")
            by_lang[lang] = by_lang.get(lang, 0) + 1

    # Pass 2: fill refcounts now that the global frequency is complete.
    def _refcount(name: str) -> int:
        return max(freq.get(name, 1) - 1, 0)

    for record in records:
        for fn in record.get("functions", []):
            fn["refcount"] = _refcount(fn["name"])
        for cls in record.get("classes", []):
            cls["refcount"] = _refcount(cls["name"])
            for m in cls.get("methods", []):
                m["refcount"] = _refcount(m["name"])

    # Write in the repository output directory, then replace the destination.
    # This prevents concurrent refreshes from leaving a partial JSONL file.
    with tempfile.NamedTemporaryFile(
        "w", dir=output.parent, prefix=f".{output.name}.", delete=False
    ) as out:
        temporary_output = Path(out.name)
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
    temporary_output.replace(output)

    rel_output = (
        output.relative_to(source_root)
        if str(output).startswith(str(source_root))
        else output
    )
    print(f"inventory: {len(records)} files -> {rel_output}", file=sys.stderr)
    for lang, n in sorted(by_lang.items()):
        print(f"  {lang}: {n}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
