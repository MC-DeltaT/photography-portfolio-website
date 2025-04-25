from dataclasses import dataclass
from functools import partial
import logging
from multiprocessing.pool import ThreadPool
from operator import call
from pathlib import Path, PurePosixPath
from typing import Callable

from buildtool.build.common import BuildContext, BuildDirectory, BuildState
from buildtool.image import open_image_file, reencode_image
from buildtool.resource.image import get_image_resources
from buildtool.types import ImageID, ImageSrcSet, PhotoID, Size, URLPath
from buildtool.url import PHOTO_IMAGE_DIR, get_image_base_url, get_image_srcset_url


logger = logging.getLogger(__name__)


def build_all_image_assets(context: BuildContext) -> None:
    logger.info('Building image assets')

    build_operations: list[Callable[[], None]] = []

    for full_path, relative_path in get_image_resources(context.resources_path):
        image_id = get_image_id(relative_path)
        # Note we don't build the original image as that won't be needed with srcsets.
        # One of the srcset resized images will be picked as the default.
        build_operations.append(partial(build_image_srcset_assets,
            context.build_dir, full_path, image_id, get_image_base_url(image_id), context.state, fast=context.fast))

    for photo in context.photos:
        image_id = get_photo_image_id(photo.id)
        context.state.photo_id_to_image_id[photo.id] = image_id
        # We do build the original here because it will be available for download on the site.
        build_operations.append(partial(build_image_srcset_assets,
            context.build_dir, photo.source_path,
            image_id,
            get_image_base_url(image_id), context.state,
            build_original=True, image_size=photo.size_px, fast=context.fast))

    with ThreadPool() as pool:
        pool.map(call, build_operations)


def get_image_id(relative_path: Path) -> ImageID:
    normalised_path = PurePosixPath(relative_path)
    assert not normalised_path.is_absolute()
    return ImageID(str(normalised_path))


def get_photo_image_id(photo_id: PhotoID) -> ImageID:
    assert '/' not in photo_id and '\\' not in photo_id
    return ImageID(f'{PHOTO_IMAGE_DIR}/{photo_id}')


@dataclass(frozen=True)
class ImageSrcSetSpec:
    max_width: int
    quality: int
    fast: bool
    priority: int   # Lower is higher priority.


IMAGE_SRCSET_SPEC = (
    ImageSrcSetSpec(2000, 85, False, 3),
    ImageSrcSetSpec(1100, 80, False, 0),
    ImageSrcSetSpec(800, 75, False, 1),
    ImageSrcSetSpec(650, 70, True, 2),
    ImageSrcSetSpec(500, 65, True, 4),
    ImageSrcSetSpec(300, 60, True, 5),
    # ImageSrcSetSpec(200, 60, True, 6),
)


def build_image_srcset_assets(build_dir: BuildDirectory, image_path: Path, image_id: ImageID, base_url: URLPath,
        state: BuildState, build_original: bool = False, image_size: Size | None = None, *, fast: bool = False) -> None:
    logger.info(f'Building image srcset assets: "{image_path}"')
    
    if build_original:
        build_dir.build_file(image_path, base_url)
    
    if image_size is None:
        image = open_image_file(image_path)
        image_size = Size((image.width, image.height))

    if fast:
        # Reencoding the images takes a while due because they are quite large.
        # If "fast" mode is enabled, create a dummy srcset with only the original image, which skips reencoding.
        srcset_descriptor = f'{image_size[0]}w'
        url = get_image_srcset_url(base_url, srcset_descriptor)
        build_dir.build_file(image_path, url)
        srcset_entries = [(0, ImageSrcSet.Entry(url, image_size, srcset_descriptor))]
    else:
        # Strategy to improve performance is to initially reencode the image to the largest srcset size, then use that
        # as the base image for subsequent reencodings.
        # Also, for the smallest size, use the next smallest image for reencoding, because it's probably small enough
        # that quality barely matters.
        # This improves performance significantly because the original image may be very large.

        # List of (priority, entry) tuples.
        srcset_entries: list[tuple[int, ImageSrcSet.Entry]] = []
        reencoding_base_image: Path | None = None
        prev_dest_path: Path | None = None
        for spec_idx, spec in enumerate(sorted(IMAGE_SRCSET_SPEC, key=lambda s: s.max_width, reverse=True)):
            # Only need to do anything if the new size is smaller than the original image.
            # Upsampling is pointless, only wastes space.
            if spec.max_width <= image_size[0]:
                new_size = calculate_new_image_size(image_size, spec.max_width)
                srcset_descriptor = f'{new_size[0]}w'
                url = get_image_srcset_url(base_url, srcset_descriptor)
                logger.info(f'Build image srcset asset URL: {url}')
                dest_path = build_dir.prepare_file(url.fs_path)
                logger.debug(f'Image srcset size: max_width={spec.max_width} size={new_size} quality={spec.quality}')
                if reencoding_base_image is None:
                    # For largest size: reencode from the original image.
                    reencoding_src_path = image_path
                    reencoding_base_image = dest_path
                elif spec_idx == len(IMAGE_SRCSET_SPEC) - 1 and prev_dest_path is not None:
                    # For smallest size: reencode from the 2nd smallest image.
                    reencoding_src_path = prev_dest_path
                else:
                    # For all other sizes: reencode from the largest reencoded image.
                    reencoding_src_path = reencoding_base_image
                logger.debug(f'Reencoding image: "{reencoding_src_path}" -> "{dest_path}"')
                if not build_dir.dry_run:
                    reencode_image(reencoding_src_path, dest_path, spec.max_width, None, spec.quality, spec.fast)
                srcset_entries.append((spec.priority, ImageSrcSet.Entry(url, new_size, srcset_descriptor)))
                prev_dest_path = dest_path

    if not srcset_entries:
        raise RuntimeError('Empty image srcset')

    # Save the resulting srcset assets for later when embedding URLs in pages,
    # since other it's not easy to know what image sizes we computed here.
    if image_id in state.image_srcsets:
        # Probably a bug if we're overwriting.
        raise RuntimeError(f'Duplicate image srcset: {image_id}')
    sorted_entries = sorted(srcset_entries, key=lambda e: e[0])
    state.image_srcsets[image_id] = ImageSrcSet(tuple(entry for _, entry in sorted_entries), 0, image_size)


def calculate_new_image_size(image_size: Size, max_width: int) -> Size:
    width, height = image_size
    assert max_width <= width
    aspect_ratio = width / height
    new_width = max_width
    # This might be off by 1, but that's probably fine for the browser.
    new_height = round(new_width / aspect_ratio)
    return Size((new_width, new_height))
