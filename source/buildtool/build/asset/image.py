from dataclasses import dataclass
import logging
from pathlib import Path

from buildtool.build.common import BuildContext, BuildDirectory, BuildState
from buildtool.image import open_image_file, reencode_image
from buildtool.resource.image import get_image_resources
from buildtool.types import ImageBaseURL, ImageSrcSet, Size
from buildtool.url import create_image_base_url, create_image_srcset_url, create_photo_base_url


logger = logging.getLogger(__name__)


def build_all_image_assets(context: BuildContext) -> None:
    logger.info('Building image assets')

    # TODO: parallelise this

    for full_path, relative_path in get_image_resources(context.resources_path):
        # Note we don't build the original image as that won't be needed with srcsets.
        # One of the srcset resized images will be picked as the default.
        build_image_srcset_assets(
            context.build_dir, full_path, create_image_base_url(relative_path), context.state)

    for photo in context.photos:
        # We do build the original here because it will be available for download on the site.
        build_image_srcset_assets(
            context.build_dir, photo.source_path,
            create_photo_base_url(photo.id, photo.file_extension), context.state,
            build_original=True, image_size=photo.size_px)


@dataclass(frozen=True)
class ImageSrcSetSpec:
    max_dimension: int
    quality: int


IMAGE_SRCSET_SPEC = (
    ImageSrcSetSpec(1500, 85),
    ImageSrcSetSpec(2000, 85),
    ImageSrcSetSpec(1000, 80),
    ImageSrcSetSpec(500, 75),
)
"""In order of priority, highest to lowest."""


def build_image_srcset_assets(build_dir: BuildDirectory, image_path: Path, base_url: ImageBaseURL, state: BuildState,
        build_original: bool = False, image_size: Size | None = None) -> None:
    if build_original:
        build_dir.build_file(image_path, base_url)
    
    if image_size is None:
        image = open_image_file(image_path)
        image_size = Size((image.width, image.height))

    srcset_entries: list[ImageSrcSet.Entry] = []
    for spec in IMAGE_SRCSET_SPEC:
        # Only need to do anything if the new size is smaller than the original image.
        # Upsampling is pointless, only wastes space.
        if spec.max_dimension <= max(image_size):
            if image_size[0] > image_size[1]:
                # Width is the constraining dimension.
                new_width = spec.max_dimension
            else:
                # Height is the constraining dimension. Need to calculate the new width after shrinking.
                # This might be off by 1, but that's probably fine for the browser.
                aspect_ratio = image_size[0] / image_size[1]
                new_width = round(aspect_ratio * spec.max_dimension)
            srcset_descriptor = f'{new_width}w'
            url = create_image_srcset_url(base_url, srcset_descriptor)
            logger.info(f'Build image srcset asset URL: {url}')
            dest_path = build_dir.prepare_file(url.fs_path)
            logger.debug(f'Image srcset size: max_dim={spec.max_dimension} width={new_width} quality={spec.quality}')
            logger.debug(f'Reencoding image: "{image_path}" -> "{dest_path}"')
            if not build_dir.dry_run:
                reencode_image(image_path, dest_path, spec.max_dimension, spec.quality)
            srcset_entries.append(ImageSrcSet.Entry(url, srcset_descriptor))
    
    if not srcset_entries:
        raise RuntimeError('Empty image srcset')

    # Save the resulting srcset assets for later when embedding URLs in pages,
    # since other it's not easy to know what image sizes we computed here.
    if base_url in state.image_srcsets:
        # Probably a bug if we're overwriting.
        raise RuntimeError(f'Duplicate image srcset: {base_url}')
    state.image_srcsets[base_url] = ImageSrcSet(tuple(srcset_entries), default_index=0)
