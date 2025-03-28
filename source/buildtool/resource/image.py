from collections.abc import Iterable
from pathlib import Path

from buildtool.utility import find_files


SUPPORTED_IMAGE_EXTENSIONS = (
    '.jpeg',
    '.jpg',
    '.png'
)


def get_image_resources_path(resources_path: Path) -> Path:
    return resources_path / 'image'


def get_image_resources(resources_path: Path) -> Iterable[tuple[Path, Path]]:
    """Yields (full_path, relative_path)"""

    root = get_image_resources_path(resources_path)
    for file in find_files(root, SUPPORTED_IMAGE_EXTENSIONS):
        yield file, file.relative_to(root)
