"""Tests for main CLI components."""
import contextlib
from pathlib import Path

import pytest  # pyre-ignore[21]
from _pytest.capture import CaptureFixture  # pyre-ignore[21]

from nbdefs.__main__ import main
from tests.test_io import FUNCS, NBPATH


@pytest.mark.parametrize("args", ["-h", "--help"])
def test_help(capsys: CaptureFixture, args: str) -> None:  # pyre-ignore[11]
    """Ensure module definition is correct in `--help`."""
    with contextlib.suppress(SystemExit):
        main([args])
    output = capsys.readouterr().out
    assert "Extract definitions from notebooks." in output


def test_cli(tmp_path: Path) -> None:
    """Ensure module definition is correct in `--help`."""
    target = tmp_path / "target.py"
    with contextlib.suppress(SystemExit):
        main([str(NBPATH), str(target)])
    assert target.read_text("utf-8") == "\n\n".join(FUNCS.values())
