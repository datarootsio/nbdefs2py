"""Test extracting functions."""
from pathlib import Path

import nbformat

from nbfuncs.extract import FuncExtractorStr

TEST_NB = Path(__file__).parent / "files" / "test.ipynb"


def test_extract() -> None:
    """Extract functions from a source file."""
    nb = nbformat.read(TEST_NB, as_version=4)
    assert FuncExtractorStr(nb.cells[0].source).funcs() == [
        "def another_func() -> None:\n  ...",
        "def print_this(x: str) -> None:\n  print(x)",
    ]
