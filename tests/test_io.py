"""Test extracting functions."""
from __future__ import annotations

from pathlib import Path

import pytest  # pyre-ignore[21]

from nbdefs.io import Definition, export, extract

NBPATH = Path(__file__).parent / "files" / "test.ipynb"
FUNCS = {
    "SomeClass": (
        "class SomeClass:\n"
        "    def __init__():\n"
        "        self.somethin = None\n\n"
        "    def gimme_somethin(self):\n"
        "        return self.somethin"
    ),
    "another_func": "def another_func() -> None:\n  ...",
    "funcs_for_days": (
        'def funcs_for_days(x: str, i: int) -> str:\n  """Docstring."""\n'
        '  return "x: {x}; i: {i}"'
    ),
    "print_this": "def print_this(x: str) -> None:\n  print(x)",
}


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
    """Export functions from a source to target file."""
    export(source, tmp_path / target)
    assert (tmp_path / written).read_text("utf-8") == "\n\n".join(FUNCS.values())


@pytest.mark.parametrize(
    ("source", "include", "exclude"),
    [
        (NBPATH, None, None),
        (NBPATH, ["another_func", "print_this"], None),
        (NBPATH, None, ["another_func", "print_this"]),
    ],
)
def test_extract(
    source: Path,
    include: list[str] | None,
    exclude: list[str] | None,
) -> None:
    """Extract functions from a source file."""
    _keep = include or FUNCS.keys()
    _remove = exclude or []
    assert set(extract(src=source, include=include, exclude=exclude)) == {
        Definition(name=fname, src=fsrc, path=NBPATH)
        for fname, fsrc in FUNCS.items()
        if fname in _keep and fname not in _remove
    }
