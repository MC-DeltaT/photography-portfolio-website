from collections.abc import Iterable
from pathlib import Path

from buildtool.utility import find_files


def get_js_resources_path(resources_path: Path) -> Path:
    return resources_path / 'js'


def get_js_resources(resources_path: Path) -> Iterable[tuple[Path, Path]]:
    """Yields (full_path, relative_path)"""

    root = get_js_resources_path(resources_path)
    for file in find_files(root, ('.js',)):
        yield file, file.relative_to(root)
