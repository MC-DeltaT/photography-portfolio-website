import logging
import shutil

from ..url import get_photo_asset_url
from ..photo_info import PhotoInfo
from .common import BuildContext, BuildDirectory


logger = logging.getLogger(__name__)


def build_photo_asset(build_dir: BuildDirectory, photo_info: PhotoInfo, *, dry_run: bool) -> None:
    url = get_photo_asset_url(photo_info.unique_id, photo_info.file_extension)
    logger.info(f'Building photo asset URL: {url}')
    dest_path = build_dir.prepare_file(url.fs_path)
    source_path = photo_info.source_path
    logger.debug(f'Copying photo: "{source_path}" -> "{dest_path}"')
    if dest_path.exists():
        raise RuntimeError(f'Photo file already exists in output (possibly duplicate name): "{dest_path}"')
    if not dry_run:
        shutil.copy(source_path, dest_path)


def build_photo_assets(context: BuildContext) -> None:
    for photo in context.photos:
        build_photo_asset(context.build_dir, photo, dry_run=context.dry_run)
