"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import argparse
import datetime
import json
import logging
import os
import sys

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251ADB126"
FIRST_NAME = "Nigar"
LAST_NAME = "Mammadrzayeva"


class RuntimeProblem(Exception):
    """A problem that must end the run with exit code 1."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flight_parser.py", allow_abbrev=False,
        description="Validate flight schedule CSV files, store them as a "
                    "JSON database and run queries against it.")
    parser.add_argument("-i", metavar="FILE", help="parse a single CSV file")
    parser.add_argument("-d", metavar="FOLDER", help="parse every .csv file in a folder")
    parser.add_argument("-j", metavar="FILE", help="load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", help="airport list file (required with -i and -d)")
    parser.add_argument("-o", metavar="FILE", help="output path of the JSON database (default: db.json)")
    parser.add_argument("-q", metavar="FILE", help="JSON file with queries to run")
    parser.add_argument("-r", metavar="FOLDER", help="folder for the response file (default: current directory)")
    return parser


def read_json(path: str, what: str):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except OSError as e:
        raise RuntimeProblem(f"cannot read {what} '{path}': {e.strerror or e}")
    except (ValueError, RecursionError) as e:
        raise RuntimeProblem(f"{what} '{path}' is not valid JSON: {e}")


def csv_paths(args) -> list[str]:
    if args.i is not None:
        if not os.path.isfile(args.i):
            raise RuntimeProblem(f"CSV file '{args.i}' does not exist or is not a file")
        return [args.i]
    if not os.path.isdir(args.d):
        raise RuntimeProblem(f"folder '{args.d}' does not exist or is not a folder")
    try:
        names = sorted(n for n in os.listdir(args.d)
                       if n.endswith(".csv") and os.path.isfile(os.path.join(args.d, n)))
    except OSError as e:
        raise RuntimeProblem(f"cannot read folder '{args.d}': {e.strerror or e}")
    if not names:
        raise RuntimeProblem(f"folder '{args.d}' contains no .csv files")
    return [os.path.join(args.d, n) for n in names]


def parse_and_store(args) -> list[dict]:
    """-i / -d: parse CSVs, write the database and errors.log."""
    try:
        airports = load_airports(args.a)
    except OSError as e:
        raise RuntimeProblem(f"cannot read airport file '{args.a}': {e.strerror or e}")
    except UnicodeDecodeError as e:
        raise RuntimeProblem(f"airport file '{args.a}' is not valid UTF-8: {e}")
    paths = csv_paths(args)
    try:
        records, errors = parse_files(paths, airports)
    except OSError as e:
        raise RuntimeProblem(f"cannot read CSV file: {e.strerror or e}: {e.filename}")
    except UnicodeDecodeError as e:
        raise RuntimeProblem(f"CSV file is not valid UTF-8: {e}")

    db_path = args.o if args.o is not None else "db.json"
    log_path = os.path.join(os.path.dirname(os.path.abspath(db_path)), "errors.log")

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    handler = None
    try:
        handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
        logger.info("Parsed %d file(s): %d valid, %d invalid",
                    len(paths), len(records), len(errors))
        for message in errors:
            logger.warning(message)
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise RuntimeProblem(f"cannot write output: {e.strerror or e}: {e.filename}")
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()
    print(f"{len(records)} valid flights written to {db_path}; "
          f"{len(errors)} invalid rows logged to {log_path}")
    return records


def load_database(path: str) -> list[dict]:
    data = read_json(path, "database")
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        raise RuntimeProblem(f"database '{path}' must be a JSON array of objects")
    return data


def run_query_file(db: list[dict], args) -> None:
    queries = read_json(args.q, "query file")
    if not isinstance(queries, (dict, list)):
        raise RuntimeProblem(f"query file '{args.q}' must be a JSON object or array")
    response = run_queries(db, queries)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
    folder = args.r if args.r is not None else "."
    path = os.path.join(folder, name)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(response, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise RuntimeProblem(f"cannot write response file: {e.strerror or e}: {e.filename}")
    print(f"{len(response)} query result(s) written to {path}")


def run(argv: list[str] | None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    sources = [s for s in (args.i, args.d, args.j) if s is not None]
    if len(sources) != 1:
        parser.error("exactly one of -i, -d or -j is required")
    if args.j is None and args.a is None:
        parser.error("-a is required with -i and -d")
    if args.j is not None and args.o is not None:
        parser.error("-o cannot be used with -j")

    try:
        db = load_database(args.j) if args.j is not None else parse_and_store(args)
        if args.q is not None:
            run_query_file(db, args)
    except RuntimeProblem as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2)."""
    try:
        return run(argv)
    except SystemExit as e:  # argparse usage errors and -h
        if e.code is None:
            return 0
        return e.code if isinstance(e.code, int) else 2
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
