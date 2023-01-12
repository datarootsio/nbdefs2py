"""Extract functions from notebooks."""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
from pathlib import Path

import nbformat


@dataclass
class SubStrBound:
    """Bounds of a string to be extracted."""

    start_ln: int
    end_ln: int
    start_col: int
    end_col: int


class FuncExtractor(ast.NodeVisitor):
    """AST node visitor to extract functions from arbitrary text."""

    def __init__(
        self: FuncExtractor,
        src: str,
    ) -> None:
        """Add empty bounds - find when visiting AST tree."""
        self.func_bounds: list[SubStrBound] = []
        self.src = src

    @staticmethod
    def _substr(
        s: str, *, start_ln: int, end_ln: int, start_col: int, end_col: int
    ) -> str:
        """Get a substring from start and end lines and columns."""
        lines = s.splitlines()[start_ln - 1 : end_ln]
        lines[0] = lines[0][start_col:]
        lines[-1] = lines[-1][:end_col]
        return "\n".join(lines)

    def visit_FunctionDef(  # noqa: N802
        self: FuncExtractor, node: ast.FunctionDef
    ) -> ast.FunctionDef:
        """Add function string bounds to `self.func_bounds`."""
        self.func_bounds.append(
            SubStrBound(
                start_ln=node.lineno,
                end_ln=node.end_lineno or -1,
                start_col=node.col_offset,
                end_col=node.end_col_offset or -1,
            )
        )
        return node

    def funcs(self: FuncExtractor) -> list[str]:
        """Extract the function defitions from the rest of the string."""
        self.visit(ast.parse(self.src))
        return [self._substr(self.src, **asdict(bound)) for bound in self.func_bounds]


test = Path(__file__).parents[1] / "tests" / "files" / "test.ipynb"
nb = nbformat.read(test, as_version=4)
