from collections.abc import Sequence
from dataclasses import dataclass
import logging
from pathlib import Path

from buildtool.build.common import BuildDirectory
from buildtool.image import reencode_image
from buildtool.types import ImageSrcSet, Size, URLPath
from buildtool.url import create_image_srcset_url


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImageSrcSetSpec:
    max_dimension: int
    quality: int


def build_image_srcset_assets(build_dir: BuildDirectory, image_path: Path, image_size: Size,
        srcset_spec: Sequence[ImageSrcSetSpec], base_url: URLPath) -> list[ImageSrcSet.Entry]:
    srcset_entries: list[ImageSrcSet.Entry] = []
    for spec in srcset_spec:
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

    return srcset_entries
