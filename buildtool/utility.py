from collections.abc import Collection, Iterator
import datetime as dt
from pathlib import Path
import os

import dateutil.parser


def remove_dashes(s: str) -> str:
    return s.replace('-', '').replace('_', '')


def find_files(root: Path, extensions: Collection[str]) -> Iterator[Path]:
    for dir_path, _subdirs, files in os.walk(root):
        dir_path = Path(dir_path)
        file_paths = [dir_path / f for f in files]
        if extensions:
            file_paths = [f for f in file_paths if f.suffix in extensions]
        yield from file_paths


def parse_datetime(s: str) -> dt.datetime:
    """A better parser than dateutil.parser.parse.
        Works for some formats that dateutil doesn't support."""
    
    # Seems to be a common date format, so we'll check it first.
    try:
        return dt.datetime.strptime(s, '%Y:%m:%d %H:%M:%S')
    except ValueError:
        pass
    # Stupid parser fills in the current time as a default if it can't parse the string.
    # So we need to detect that case by parsing with different defaults and see if any of the default gets used.
    datetime = dateutil.parser.parse(s, default=dt.datetime(1901, 1, 1, 1, 1, 1, 1))
    datetime2 = dateutil.parser.parse(s, default=dt.datetime(1902, 2, 2, 2, 2, 2, 2))
    if datetime == datetime2:
        return datetime
    raise ValueError(f'Could not parse datetime: {s}')
