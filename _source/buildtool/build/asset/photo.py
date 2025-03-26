import logging
import shutil

from ...image import reencode_image
from ...types import ImageSrcSet
from ...url import get_photo_asset_url
from ...photo_info import PhotoInfo
from ..common import BuildContext, BuildDirectory, BuildState


logger = logging.getLogger(__name__)


IMAGE_SRCSET_SPEC = (
    (1500, 85),
    (2000, 85),
    (1000, 80),
    (500, 75),
)
"""List of (max_dimension, jpg_quality). In order of priority, highest to lowest."""


def build_photo_original_asset(build_dir: BuildDirectory, photo: PhotoInfo, *, dry_run: bool) -> None:
    url = get_photo_asset_url(photo.unique_id, photo.file_extension, None)
    logger.info(f'Building photo asset URL: {url}')
    dest_path = build_dir.prepare_file(url.fs_path)
    source_path = photo.source_path
    logger.debug(f'Copying photo: "{source_path}" -> "{dest_path}"')
    if not dry_run:
        shutil.copy(source_path, dest_path)


def build_photo_srcset_assets(build_dir: BuildDirectory, photo: PhotoInfo, state: BuildState, *, dry_run: bool) -> None:
    srcset_entries: list[ImageSrcSet.Entry] = []
    for max_dimension, quality in IMAGE_SRCSET_SPEC:
        # Only need to do anything if the new size is smaller than the original image.
        # Upsampling is pointless, only wastes space.
        if max_dimension <= max(photo.size_px):
            if photo.size_px[0] > photo.size_px[1]:
                # Width is the constraining dimension.
                new_width = max_dimension
            else:
                # Height is the constraining dimension. Need to calculate the new width after shrinking.
                # This might be off by 1, but that's probably fine for the browser.
                aspect_ratio = photo.size_px[0] / photo.size_px[1]
                new_width = round(aspect_ratio * max_dimension)
            srcset_descriptor = f'{new_width}w'
            url = get_photo_asset_url(photo.unique_id, photo.file_extension, srcset_descriptor)
            logger.info(f'Build photo srcset asset URL: {url}')
            dest_path = build_dir.prepare_file(url.fs_path)
            source_path = photo.source_path
            logger.debug(f'Photo srcset size: max_dim={max_dimension} width={new_width} quality={quality}')
            logger.debug(f'Reencoding photo: "{source_path}" -> "{dest_path}"')
            if not dry_run:
                reencode_image(source_path, dest_path, max_dimension, quality)
            srcset_entries.append(ImageSrcSet.Entry(url, srcset_descriptor))
    
    if not srcset_entries:
        raise RuntimeError('Empty photo srcset')

    # Save the resulting srcset assets for later when embedding URLs in pages,
    # since other it's not easy to know what image sizes we computed here.
    state.image_srcsets[photo.unique_id] = ImageSrcSet(tuple(srcset_entries), default_index=0)


def build_photo_assets(build_dir: BuildDirectory, photo: PhotoInfo, state: BuildState, *, dry_run: bool) -> None:
    build_photo_original_asset(build_dir, photo, dry_run=dry_run)
    build_photo_srcset_assets(build_dir, photo, state, dry_run=dry_run)


def build_all_photo_assets(context: BuildContext) -> None:
    # TODO: parallelise this, it's very slow
    for photo in context.photos:
        build_photo_assets(context.build_dir, photo, context.state, dry_run=context.dry_run)
