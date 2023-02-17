"""Tests for main CLI components."""
import contextlib
from pathlib import Path

import pytest  # pyre-ignore[21]
from _pytest.capture import CaptureFixture  # pyre-ignore[21]

from nbfuncs.__main__ import main

NBPATH = Path(__file__).parent / "files" / "test.ipynb"


@pytest.mark.parametrize("args", ["-h", "--help"])
def test_help(capsys: CaptureFixture, args: str) -> None:  # pyre-ignore[11]
    """Ensure module definition is correct in `--help`."""
    with contextlib.suppress(SystemExit):
        main([args])
    output = capsys.readouterr().out
    assert "Extract definitions from notebooks." in output
