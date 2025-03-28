from dataclasses import dataclass
import logging
from pathlib import Path, PurePosixPath

from buildtool.build.common import BuildContext, BuildDirectory, BuildState
from buildtool.image import open_image_file, reencode_image
from buildtool.resource.image import get_image_resources
from buildtool.types import ImageID, ImageSrcSet, PhotoID, Size, URLPath
from buildtool.url import PHOTO_IMAGE_DIR, get_image_base_url, get_image_srcset_url


logger = logging.getLogger(__name__)


def build_all_image_assets(context: BuildContext) -> None:
    logger.info('Building image assets')

    # TODO: parallelise this

    for full_path, relative_path in get_image_resources(context.resources_path):
        image_id = get_image_id(relative_path)
        # Note we don't build the original image as that won't be needed with srcsets.
        # One of the srcset resized images will be picked as the default.
        build_image_srcset_assets(
            context.build_dir, full_path, image_id, get_image_base_url(image_id), context.state)

    for photo in context.photos:
        image_id = get_photo_image_id(photo.id)
        context.state.photo_id_to_image_id[photo.id] = image_id
        # We do build the original here because it will be available for download on the site.
        build_image_srcset_assets(
            context.build_dir, photo.source_path,
            image_id,
            get_image_base_url(image_id), context.state,
            build_original=True, image_size=photo.size_px)


def get_image_id(relative_path: Path) -> ImageID:
    normalised_path = PurePosixPath(relative_path)
    assert not normalised_path.is_absolute()
    return ImageID(str(normalised_path))


def get_photo_image_id(photo_id: PhotoID) -> ImageID:
    assert '/' not in photo_id and '\\' not in photo_id
    return ImageID(f'{PHOTO_IMAGE_DIR}/{photo_id}')


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


def build_image_srcset_assets(build_dir: BuildDirectory, image_path: Path, image_id: ImageID, base_url: URLPath,
        state: BuildState, build_original: bool = False, image_size: Size | None = None) -> None:
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
            url = get_image_srcset_url(base_url, srcset_descriptor)
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
    if image_id in state.image_srcsets:
        # Probably a bug if we're overwriting.
        raise RuntimeError(f'Duplicate image srcset: {image_id}')
    state.image_srcsets[image_id] = ImageSrcSet(tuple(srcset_entries), default_index=0)
