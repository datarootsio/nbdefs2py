"""Test extracting functions."""
from pathlib import Path

import nbformat

from nbdefs.funcs import FuncExtractorStr, from_nb

TEST_NB = Path(__file__).parent / "files" / "test.ipynb"


def test_extract_str() -> None:
    """Extract functions from a source string."""
    nb = nbformat.read(TEST_NB, as_version=4)
    assert FuncExtractorStr(nb.cells[0].source).funcs() == {
        "another_func": "def another_func() -> None:\n  ...",
        "print_this": "def print_this(x: str) -> None:\n  print(x)",
    }


def test_from_nb() -> None:
    """Extract functions from a notebook file."""
    nb = nbformat.read(TEST_NB, as_version=4)
    assert from_nb(nb) == [
        {
            "another_func": "def another_func() -> None:\n  ...",
            "print_this": "def print_this(x: str) -> None:\n  print(x)",
        },
        {},
        {
            "funcs_for_days": (
                "def funcs_for_days(x: str, i: int) -> str:\n"
                '  """Docstring."""\n  return "x: {x}; i: {i}"'
            ),
        },
    ]
