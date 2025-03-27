from collections.abc import Collection, Iterator
from pathlib import Path


def remove_dashes(s: str) -> str:
    return s.replace('-', '').replace('_', '')


def find_files(root: Path, extensions: Collection[str]) -> Iterator[Path]:
    for dir_path, _subdirs, files in root.walk():
        file_paths = [dir_path / f for f in files]
        if extensions:
            file_paths = [f for f in file_paths if f.suffix in extensions]
        yield from file_paths
