from collections.abc import Collection, Iterator
import datetime as dt
from functools import cache
from pathlib import Path
import subprocess

import dateutil.parser


def remove_dashes(s: str) -> str:
    return s.replace('-', '').replace('_', '')


def find_files(root: Path, extensions: Collection[str]) -> Iterator[Path]:
    def visit_dir(dir: Path) -> Iterator[Path]:
        assert dir.is_dir()
        entries = sorted(dir.iterdir())
        files = [e for e in entries if not e.is_dir()]
        if extensions:
            files = [f for f in files if f.suffix in extensions]
        yield from files
        subdirs = [e for e in entries if e.is_dir()]
        for subdir in subdirs:
            yield from visit_dir(subdir)

    yield from visit_dir(root)


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


@cache
def get_latest_commit_date() -> dt.datetime:
    return dt.datetime.fromtimestamp(
        int(subprocess.run(
            ['git', 'log', '-1', '--format=%at'],
            check=True, stdout=subprocess.PIPE, encoding='utf-8').stdout.strip()),
        dt.timezone.utc)
