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
        self.func_bounds: dict[str, SubStrBound] = {}
        self.src = src

    @staticmethod
    def _substr(
        s: str,
        *,
        start_ln: int,
        end_ln: int,
        start_col: int,
        end_col: int,
    ) -> str:
        """Get a substring from start and end lines and columns."""
        lines = s.splitlines()[start_ln - 1 : end_ln]
        lines[0] = lines[0][start_col:]
        lines[-1] = lines[-1][:end_col]
        return "\n".join(lines)

    def visit_FunctionDef(  # noqa: N802
        self: FuncExtractorStr,
        node: ast.FunctionDef,
    ) -> ast.FunctionDef:
        """Add function string bounds to `self.func_bounds`."""
        self.func_bounds[node.name] = SubStrBound(
            start_ln=node.lineno,
            end_ln=node.end_lineno or -1,
            start_col=node.col_offset,
            end_col=node.end_col_offset or -1,
        )

        return node

    def funcs(self: FuncExtractorStr) -> dict[str, str]:
        """Extract the function definitions from the rest of the string."""
        self.visit(ast.parse(self.src))
        return {
            func: self._substr(self.src, **asdict(bound))
            for func, bound in self.func_bounds.items()
        }


def from_nb(nb: NotebookNode) -> list[dict[str, str]]:
    """Extract functions from notebook code cells."""
    return [
        FuncExtractorStr(cell.source).funcs()
        for cell in nb.cells
        if cell.cell_type == "code"
    ]


def from_src(src: str) -> dict[str, str]:
    """Extract functions from source file."""
    return FuncExtractorStr(src).funcs()


def from_obj(obj: str | NotebookNode) -> list[dict[str, str]]:
    """Extract functions from object (string or notebook)."""
    return [from_src(obj)] if isinstance(obj, str) else from_nb(obj)
