<p align="center">
  <a href="https://github.com/datarootsio/nbdefs2py"><img alt="logo" src="https://raw.githubusercontent.com/datarootsio/nbdefs2py/main/logo.png"></a>
</p>

[![PyPI - Version](https://img.shields.io/pypi/v/nbdefs.svg)](https://pypi.org/project/nbdefs2py)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/nbdefs2py.svg)](https://pypi.org/project/nbdefs2py)

-----

> A small package (only) to export functions and classes from notebooks to scripts

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install nbdefs2py
```

## Usage

`nbdefs2py` can be used as a CLI tool or a Python function.

```console
$ python -m nbdefs2py -h
usage: python -m nbfuncs [-h] [-i IGNORE] [--update] [--no-update] [--include INCLUDE [INCLUDE ...]]
                         [--exclude EXCLUDE [EXCLUDE ...]]
                         SRC DST

Extract definitions from notebooks.

positional arguments:
  SRC                   source file/path
  DST                   target file/path

optional arguments:
  -h, --help            show this help message and exit
  -i IGNORE, --ignore IGNORE
                        glob expression of files to ignore
  --update              update only existing functions
  --no-update           overwrite destination file
  --include INCLUDE [INCLUDE ...]
                        names of functions to include
  --exclude EXCLUDE [EXCLUDE ...]
                        names of functions to ignore
```

```python3
>>> from nbdefs2py.io import export
>>> export(source="nb.ipynb", destination="exported.py")
```

## License

`nbdefs2py` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
