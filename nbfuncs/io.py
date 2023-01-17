"""Wrap extract function logic to files."""
from __future__ import annotations

import errno
import os
from dataclasses import dataclass
from functools import reduce
from itertools import groupby
from pathlib import Path
from typing import Any

import nbformat

from nbfuncs.extract import extract_funcs_nb


@dataclass
class Function:
    """Function representation from source file."""

    name: str
    path: Path
    src: str


class NotFoundError(FileNotFoundError):
    """Rename error since we're referring to file or directory."""


class ExistsError(FileExistsError):
    """Rename error since we're referring to file or directory."""


class FileSuffixError(Exception):
    """Invalid file extension."""

    def __init__(self: FileSuffixError, file: Path, message: str | None = None) -> None:
        """Print message and file."""
        super().__init__(f"{message or self.__doc__} Got `{file.suffix}`.")


class PathNameError(Exception):
    """Path name does not match expected."""

    def __init__(self: PathNameError, src: Path, dest: Path) -> None:
        """Include path type (file or directory) and suffix."""
        super().__init__(
            f"'{str(src)}' is a {'directory' if src.is_dir() else 'file'}"
            f" and '{str(dest)}' has '{dest.suffix}' suffix."
            " If this is the desired behavior, pass `check_pathnames=False`"
        )


def extract_funcs(
    src: Path | str,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    **read_kwargs: Any,  # noqa: ANN401
) -> list[Function]:
    """
    Extract functions from `src` and write to `dest`.

    :param src: source location (file or directory)
    :param include: functions to include (`None` for all), defaults to `None`
    :param exclude: functions to exclude (`None` for none), defaults to `None`
    :param read_kwargs: keyword arguments to pass to `nbformat.read`
    :raises NotFoundError: when source is not found
    :raises FileSuffixError: when source file is not a notebook (`.ipynb`)
    :raises ExistsError: when destination exists and `overwrite=False`
    """
    src = Path(src)

    if not src.exists():
        raise NotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), src)
    if src.is_file() and src.suffix != ".ipynb":
        raise FileSuffixError(src)

    if all(arg is not None for arg in (include, exclude)):
        raise ValueError("Must specify exactly one of `include` or `exclude`.")

    nb_paths = list(src.rglob("*.ipynb")) if src.is_dir() else [src]
    nbs = {
        path: nbformat.read(path, **{"as_version": 4, **read_kwargs})
        for path in nb_paths
    }

    funcs = [
        Function(
            name=func_name,
            path=path,
            src=func_src,
        )
        for path, node in nbs.items()
        for func_name, func_src in reduce(
            lambda d1, d2: {**d1, **d2}, extract_funcs_nb(node), {}
        ).items()
    ]

    if all(arg is None for arg in (include, exclude)):
        return funcs
    keep = include or ({f.name for f in funcs} - set(exclude))  # pyre-ignore[6]
    return [func for func in funcs if func.name in keep]


def export(
    src: Path | str,
    dest: Path | str,
    *,
    overwrite: bool = False,
    check_pathnames: bool = True,
    **extract_kwargs: Any,  # noqa: ANN401
) -> None:
    """
    Export functions from notebook(s) `src` to `dest`.

    :param src: source location (file or directory)
    :param dest: destination location (file or directory)
    :param overwrite: overwrite destination - if exists, defaults to `False`
    :param extract_kwargs: keyword arguments to pass to `extract`
    """
    src = Path(src)
    dest = Path(dest)
    if check_pathnames and src.is_file() ^ bool(dest.suffix):
        raise PathNameError(src, dest)

    if dest.exists() and not overwrite:
        raise ExistsError(
            errno.EEXIST,
            "Destination already exists. Pass `overwrite=True` overwrite file(s).",
            dest,
        )

    if src.is_file():
        dest.touch(exist_ok=True)
    else:
        dest.mkdir(parents=True, exist_ok=True)

    funcs = extract_funcs(src=src, **extract_kwargs)
    for _path, _funcs in groupby(
        sorted(funcs, key=lambda e: e.path), key=lambda e: e.path
    ):
        target = (dest / _path.relative_to(src)).with_suffix(".py")
        target.touch(exist_ok=True)
        target.write_text("\n\n".join((f.src for f in _funcs)))
