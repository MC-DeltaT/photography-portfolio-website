from collections import Counter
from collections.abc import Sequence
import logging
from pathlib import Path
import shutil

from .photo_info import PhotoInfo, read_photo_info
from .resource.common import get_resources_path
from .resource.photo import find_photos, get_photo_resource_path
from .url import get_photo_asset_url


logger = logging.getLogger(__name__)


class BuildDirectory:
    def __init__(self, root: Path, *, dry_run: bool) -> None:
        self.root = root
        self.dry_run = dry_run

    def clean(self) -> None:
        logger.info(f'Deleting build directory: "{self.root}"')
        if not self.dry_run:
            if self.root.exists():
                shutil.rmtree(self.root, ignore_errors=False)

    def prepare_directory(self, dir_path: str | Path) -> Path:
        """Given a relative directory path, ensures that directory exists in the build directory.
            Returns the absolute path of the directory."""

        dir_path = Path(dir_path)
        if dir_path.is_absolute():
            raise ValueError('dir_path cannot be an absolute path')
        path = self.root / dir_path
        logger.debug(f'Creating build directory: "{path}"')
        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)
        return path

    def prepare_file(self, file_path: str | Path) -> Path:
        """Given a relative file path, ensures the parent directory exists in the build directory.
            Returns the absolute path of the file."""

        file_path = Path(file_path)
        abs_dir_path = self.prepare_directory(file_path.parent)
        return abs_dir_path / file_path.name


def build_photo_asset(build_dir: BuildDirectory, photo_info: PhotoInfo, *, dry_run: bool) -> None:
    url = get_photo_asset_url(photo_info.unique_id, photo_info.file_extension)
    logger.info(f'Creating photo asset URL: {url}')
    dest_path = build_dir.prepare_file(url.fs_path)
    source_path = photo_info.source_path
    logger.debug(f'Copying photo: "{source_path}" -> "{dest_path}"')
    if dest_path.exists():
        raise RuntimeError(f'Photo file already exists in output (possibly duplicate name): "{dest_path}"')
    if not dry_run:
        shutil.copy(source_path, dest_path)


def verify_photo_unique_ids(photo_infos: Sequence[PhotoInfo]) -> None:
    id_counts = Counter(p.unique_id for p in photo_infos)
    duplicated = [i for i, count in id_counts.items() if count > 1]
    if duplicated:
        # Unlikely to occur so it's fine to force the user to fix it manually.
        raise RuntimeError(f'Duplicate photo unique IDs: {duplicated}')


def run_build(build_path: Path, data_path: Path, *, dry_run: bool) -> None:
    logger.info(f'Build directory: "{build_path}"')
    logger.info(f'Data directory: "{data_path}"')

    build_dir = BuildDirectory(build_path, dry_run=dry_run)
    build_dir.clean()

    resources_path = get_resources_path(data_path)
    photo_resources_path = get_photo_resource_path(resources_path)

    photo_resource_records = find_photos(photo_resources_path)

    photo_infos = [read_photo_info(r) for r in photo_resource_records]
    # Sort by ID for stability and debuggability.
    photo_infos = sorted(photo_infos, key=lambda p: p.unique_id)

    verify_photo_unique_ids(photo_infos)

    # TODO
    for photo in photo_infos:
        build_photo_asset(build_dir, photo, dry_run=dry_run)

    ... # TODO
