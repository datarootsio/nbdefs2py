"""Extract functions from notebooks."""
from __future__ import annotations

import ast
from dataclasses import asdict, dataclass

from nbformat import NotebookNode


@dataclass
class SubStrBound:
    """Bounds of a string to be extracted."""

    start_ln: int
    end_ln: int
    start_col: int
    end_col: int


class FuncExtractorStr(ast.NodeVisitor):
    """AST node visitor to extract functions from arbitrary text."""

    def __init__(self: FuncExtractorStr, src: str) -> None:
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
        self: FuncExtractorStr, node: ast.FunctionDef
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

    def funcs(self: FuncExtractorStr) -> list[str]:
        """Extract the function definitions from the rest of the string."""
        self.visit(ast.parse(self.src))
        return [self._substr(self.src, **asdict(bound)) for bound in self.func_bounds]


def extract_funcs_nb(nb: NotebookNode) -> list[list[str]]:
    """Extract functions from notebook code cells."""
    return [
        FuncExtractorStr(cell.source).funcs()
        for cell in nb.cells
        if cell.cell_type == "code"
    ]
