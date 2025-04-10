from collections.abc import Iterable
from pathlib import Path

from buildtool.utility import find_files


def get_css_resources_path(resources_path: Path) -> Path:
    return resources_path / 'css'


def get_css_resources(resources_path: Path) -> Iterable[tuple[Path, Path]]:
    """Yields (full_path, relative_path)"""

    root = get_css_resources_path(resources_path)
    for file in find_files(root, ('.css',)):
        yield file, file.relative_to(root)
