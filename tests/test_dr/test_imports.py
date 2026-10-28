"""Guard: pure DR modules must not import the AI layer.

This is the test that keeps 'everything measurable stays in code' honest.
If someone adds `from postwise.ai import ...` to dr03, this fails.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PURE_MODULES = [
    "dr01_check",
    "dr03_voice",
    "dr04_audience",
    "dr06_rhythm",
    "dr08_score",
]
DR_DIR = Path(__file__).resolve().parents[2] / "src" / "postwise" / "dr"


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


@pytest.mark.parametrize("module", PURE_MODULES)
def test_pure_module_does_not_import_ai(module: str) -> None:
    path = DR_DIR / f"{module}.py"
    if not path.exists():
        pytest.skip(f"{module} not written yet")
    for imp in _imports_from(path):
        assert not imp.startswith("postwise.ai"), (
            f"{module} must not import {imp} — pure modules cannot touch the AI layer"
        )
