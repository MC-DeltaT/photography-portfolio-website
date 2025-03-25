import logging
import shutil

from ...types import Size
from ...url import get_photo_asset_url
from ...photo_info import PhotoInfo
from ..common import BuildContext, BuildDirectory


logger = logging.getLogger(__name__)


IMAGE_SRCSET_MAX_DIMENSIONS = (
    2000,
    1500,
    1000,
    500
)


def get_image_srcset_dimensions(image_size_px: Size) -> list[Size]:
    """Computes the resulting image sizes for the srcset for an image."""

    def apply_max_dim(max_dim: int) -> Size | None:
        if max_dim <= image_size_px[0] and max_dim <= image_size_px[1]:
            return Size((max(max_dim, image_size_px[0]), max(max_dim, image_size_px[1])))
        else:
            # Otherwise image won't be shrunk, so no need to create that size.
            return None

    result = list(filter(None, map(apply_max_dim, IMAGE_SRCSET_MAX_DIMENSIONS)))
    return result


# TODO: shrink photos

# TODO: build photo srcset with different qualities


def build_photo_asset(build_dir: BuildDirectory, photo_info: PhotoInfo, *, dry_run: bool) -> None:
    url = get_photo_asset_url(photo_info.unique_id, photo_info.file_extension)
    logger.info(f'Building photo asset URL: {url}')
    dest_path = build_dir.prepare_file(url.fs_path)
    source_path = photo_info.source_path
    logger.debug(f'Copying photo: "{source_path}" -> "{dest_path}"')
    if not dry_run:
        if dest_path.exists():
            raise RuntimeError(f'Photo file already exists in output (possibly duplicate name): "{dest_path}"')
        shutil.copy(source_path, dest_path)


def build_photo_assets(context: BuildContext) -> None:
    for photo in context.photos:
        build_photo_asset(context.build_dir, photo, dry_run=context.dry_run)
