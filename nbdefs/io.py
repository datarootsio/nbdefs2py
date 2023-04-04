"""Wrap extract function logic to files."""
from __future__ import annotations

import errno
import os
from dataclasses import dataclass
from functools import reduce
from itertools import chain, groupby
from pathlib import Path
from typing import Any, Iterable

import nbformat

from nbdefs import funcs

NB_SUFFIX = ".ipynb"
PY_SUFFIX = ".py"


@dataclass(frozen=True)
class Definition:
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


class InputsError(ValueError):
    """Invalid inputs."""

    def __init__(self: InputsError, message: str | None = None) -> None:
        """Print custom message."""
        super().__init__(message or self.__doc__)


class PathNameError(Exception):
    """Path name does not match expected."""

    def __init__(self: PathNameError, src: Path, dest: Path) -> None:
        """Include path type (file or directory) and suffix."""
        super().__init__(
            f"'{str(src)}' is a {'directory' if src.is_dir() else 'file'}"
            f" and '{str(dest)}' has '{dest.suffix}' suffix."
            " If this is the desired behavior, pass `check_pathnames=False`",
        )


def _all_eq(iterable: Iterable[Any]) -> bool:
    """
    Check that all elements in iterable are equal.

    From `itertools` recipes. Check
     `https://docs.python.org/3/library/itertools.html#itertools-recipes` for more
     information.
    """
    g = groupby(iterable)
    return bool(next(g, True)) and not next(g, False)  # noqa: FBT003


def _combine_funcs(
    src: list[Definition],
    dest: list[Definition],
    update: bool | None,
) -> Iterable[Definition]:
    """
    Combine source and destination functions according to `update` strategy.

    :param src: source functions
    :param dest: destination functions
    :param update: update destination functions, overwrite or upsert (`True`, `False`
     and `None`, respectively)
    :return: merged list of functions
    """

    def _first_match(el: Definition, funcs: list[Definition]) -> Definition | None:
        """Return first match, if exists."""
        return next((f for f in funcs if f.name == el.name), None)

    funcs_update = dest if update in (True, None) else []
    updated = filter(
        lambda f: f is not None,
        (_first_match(func, src) for func in funcs_update),
    )
    if update is None:
        return chain.from_iterable((dest, set(src) - {f for f in updated if f}))
    return dest


def extract(
    src: Path | str,
    ignore: str | None = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    **read_kwargs: Any,  # noqa: ANN401
) -> list[Definition]:
    """
    Extract functions from `src` and write to `dest`.

    :param src: source location (file or directory)
    :param ignore: glob expression of files to ignore, defaults to `None`
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
    if src.is_file() and src.suffix not in (PY_SUFFIX, NB_SUFFIX):
        raise FileSuffixError(src)

    if all(arg is not None for arg in (include, exclude)):
        raise InputsError("Must specify at least one of `include` or `exclude`.")

    ignore_glob = src.glob(ignore or "**/!*")
    paths = list(
        filter(
            lambda p: p not in ignore_glob,
            chain.from_iterable(src.rglob(f"*{s}") for s in (NB_SUFFIX, PY_SUFFIX))
            if src.is_dir()
            else [src],
        ),
    )

    if not _all_eq(path.suffix for path in paths):
        raise InputsError(
            "Expected only one file type, got"
            f" {list({path.suffix for path in paths})}.",
        )
    _src = {
        path: nbformat.read(path, **{"as_version": 4, **read_kwargs})
        if path.suffix == NB_SUFFIX
        else path.read_text()
        for path in paths
    }
    funcs_src = [
        Definition(
            name=fname,
            path=path,
            src=fsrc,
        )
        for path, node in _src.items()
        for fname, fsrc in reduce(
            lambda d1, d2: {**d1, **d2},
            funcs.from_obj(node),
            {},
        ).items()
    ]

    if all(arg is None for arg in (include, exclude)):
        return funcs_src
    keep = include or ({f.name for f in funcs_src} - set(exclude))  # pyre-ignore[6]
    return [func for func in funcs_src if func.name in keep]


def export(
    source: Path | str,
    destination: Path | str,
    *,
    update: bool | None = None,
    exist_ok: bool = True,
    check_pathnames: bool = True,
    **extract_kwargs: Any,  # noqa: ANN401
) -> None:
    """
    Export functions from notebook(s) `src` to `dest`.

    :param src: source location (file or directory)
    :param dest: destination location (file or directory)
    :param update: `True` only updates existing functions in destination, `False`
     overwrites and None will upsert functions, defaults to `None`
    :param exist_ok: allow existing destination file
    :param check_pathnames: check that files end in `.py` and directories do not
    :param extract_kwargs: keyword arguments to pass to `extract`
    """
    source = Path(source)
    destination = Path(destination)

    if check_pathnames and source.is_file() ^ bool(destination.suffix):
        raise PathNameError(source, destination)

    if destination.exists() and not exist_ok:
        raise ExistsError(
            errno.EEXIST,
            "Destination already exists and `exist_ok=False`.",
            destination,
        )

    if source.is_file():
        destination.touch(exist_ok=True)
    else:
        destination.mkdir(parents=True, exist_ok=True)

    funcs_src = extract(src=source, **extract_kwargs)
    funcs_dst = extract(src=destination)
    funcs_all = _combine_funcs(funcs_src, funcs_dst, update=update)

    for _path, _funcs in groupby(
        sorted(funcs_all, key=lambda e: e.path),
        key=lambda e: e.path,
    ):
        target = (
            (destination / _path.relative_to(source)).with_suffix(PY_SUFFIX)
            if source in (*_path.parents, _path)  # pyre-ignore[60]
            else _path
        )
        target.touch(exist_ok=True)
        target.write_text("\n\n".join(sorted(f.src for f in _funcs)))
