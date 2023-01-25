"""CLI utilities."""
import argparse

from nbfuncs.io import export

parser = argparse.ArgumentParser(
    prog="python -m nbfuncs", description="Extract functions from notebooks."
)
parser.add_argument("source", metavar="SRC", type=str, help="source file/path")
parser.add_argument("destination", metavar="DST", type=str, help="target file/path")
parser.add_argument(
    "-i", "--ignore", type=str, help="glob expression of files to ignore"
)

parser.add_argument(
    "--update", action="store_true", help="update only existing functions"
)
parser.add_argument(
    "--no-update",
    dest="update",
    action="store_false",
    help="overwrite destination file",
)
parser.add_argument(
    "--include", type=str, nargs="+", default=None, help="names of functions to include"
)
parser.add_argument(
    "--exclude", type=str, nargs="+", default=None, help="names of functions to ignore"
)

parser.set_defaults(update=None)
args = parser.parse_args()
export(*args)
