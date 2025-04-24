from collections import Counter
from collections.abc import Sequence
import logging
from pathlib import Path

from buildtool.build.asset import build_all_assets
from buildtool.build.common import BuildContext, BuildDirectory, BuildState
from buildtool.build.html import build_all_html
from buildtool.build.statistics import print_build_statistics
from buildtool.photo_collection import PhotoCollection
from buildtool.photo_info import PhotoInfo, read_photo_info
from buildtool.resource.photo import find_photos, get_photo_resources_path


logger = logging.getLogger(__name__)


def verify_photo_ids(photo_infos: Sequence[PhotoInfo]) -> None:
    id_counts = Counter(p for p in photo_infos)
    duplicated = [i for i, count in id_counts.items() if count > 1]
    if duplicated:
        # Unlikely to occur so it's fine to force the user to fix it manually.
        raise RuntimeError(f'Duplicate photo unique IDs: {duplicated}')


def run_build(build_path: Path, resources_path: Path, *, fast: bool, dry_run: bool) -> None:
    logger.info(f'Running website build')
    logger.info(f'Build directory: "{build_path}"')
    logger.info(f'Resources directory: "{resources_path}"')

    build_dir = BuildDirectory(build_path, fast=fast, dry_run=dry_run)
    build_dir.clean()

    photo_resource_records = find_photos(get_photo_resources_path(resources_path))

    photo_infos = [read_photo_info(r) for r in photo_resource_records]
    # Sort by ID for stability and debuggability.
    photo_infos = tuple(sorted(photo_infos, key=lambda p: p.id))
    verify_photo_ids(photo_infos)

    photo_collection = PhotoCollection(photo_infos)

    build_context = BuildContext(
        build_dir=build_dir, resources_path=resources_path,
        fast=fast, dry_run=dry_run,
        photos=photo_collection,
        state=BuildState())

    # Note: must build photo assets first because they generate the srcset state which is read later when building pages.
    build_all_assets(build_context)
    build_all_html(build_context)

    print_build_statistics(build_context)
