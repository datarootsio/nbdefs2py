"""Test extracting functions."""
from pathlib import Path

import pytest  # pyre-ignore[21]

from nbfuncs.io import export

NBPATH = Path(__file__).parent / "files" / "test.ipynb"
FUNCS = """\
def another_func() -> None:
  ...

def print_this(x: str) -> None:
  print(x)

def funcs_for_days(x: str, i: int) -> str:
  \"\"\"Docstring.\"\"\"
  return \"x: {x}; i: {i}\""""


@pytest.mark.parametrize(
    ("source", "target", "written"),
    [
        (NBPATH, "tmpfile.py", Path("tmpfile.py")),
        (
            NBPATH.parent,
            "tmpdir",
            Path("tmpdir") / NBPATH.with_suffix(".py").name,
        ),
    ],
)
def test_export(source: Path, target: str, written: Path, tmp_path: Path) -> None:
    """Extract functions from a source string."""
    export(source, tmp_path / target)
    assert (tmp_path / written).read_text("utf-8") == FUNCS
