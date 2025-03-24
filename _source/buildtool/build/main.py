from collections import Counter
from collections.abc import Sequence
import logging
from pathlib import Path

from ..photo_info import PhotoInfo, read_photo_info
from ..resource.common import get_resources_path
from ..resource.photo import find_photos, get_photo_resources_path
from .common import BuildContext, BuildDirectory
from .css import build_css
from .photo_asset import build_photo_assets


logger = logging.getLogger(__name__)


def verify_photo_unique_ids(photo_infos: Sequence[PhotoInfo]) -> None:
    id_counts = Counter(p.unique_id for p in photo_infos)
    duplicated = [i for i, count in id_counts.items() if count > 1]
    if duplicated:
        # Unlikely to occur so it's fine to force the user to fix it manually.
        raise RuntimeError(f'Duplicate photo unique IDs: {duplicated}')


# TODO: can probably automate building of things based on file structure


def run_build(build_path: Path, data_path: Path, *, dry_run: bool) -> None:
    logger.info(f'Running website build')
    logger.info(f'Build directory: "{build_path}"')
    logger.info(f'Data directory: "{data_path}"')

    build_dir = BuildDirectory(build_path, dry_run=dry_run)
    build_dir.clean()

    resources_path = get_resources_path(data_path)

    photo_resource_records = find_photos(get_photo_resources_path(resources_path))
    photos = [read_photo_info(r) for r in photo_resource_records]
    # Sort by ID for stability and debuggability.
    photos = sorted(photos, key=lambda p: p.unique_id)
    verify_photo_unique_ids(photos)

    build_context = BuildContext(build_dir, data_path, resources_path, dry_run, photos)

    build_css(build_context)
    build_photo_assets(build_context)

    ... # TODO
