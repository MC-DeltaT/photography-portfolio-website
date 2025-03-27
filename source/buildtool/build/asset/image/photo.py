import logging
from multiprocessing.pool import ThreadPool

from buildtool.build.asset.image.common import build_image_srcset_assets
from buildtool.build.common import BuildContext, BuildDirectory, BuildState
from buildtool.photo_info import PhotoInfo
from buildtool.types import ImageAssetID, ImageSrcSet, PhotoID
from buildtool.url import get_photo_asset_base_url


logger = logging.getLogger(__name__)


# TODO: merge photo asset building into image asset building to simplify


def get_photo_image_asset_id(photo_id: PhotoID) -> ImageAssetID:
    return ImageAssetID('photo', photo_id)


def build_photo_original_asset(build_dir: BuildDirectory, photo: PhotoInfo) -> None:
    url = get_photo_asset_base_url(photo.id, photo.file_extension)
    build_dir.build_file(photo.source_path, url)


def build_photo_srcset_assets(build_dir: BuildDirectory, photo: PhotoInfo, state: BuildState) -> None:
    base_url = get_photo_asset_base_url(photo.id, photo.file_extension)
    srcset_entries = build_image_srcset_assets(
        build_dir, photo.source_path, base_url, photo.size_px)
    # Save the resulting srcset assets for later when embedding URLs in pages,
    # since other it's not easy to know what image sizes we computed here.
    state.image_srcsets[image_id] = ImageSrcSet(tuple(srcset_entries), default_index=0)


def build_photo_assets(build_dir: BuildDirectory, photo: PhotoInfo, state: BuildState) -> None:
    build_photo_original_asset(build_dir, photo)
    build_photo_srcset_assets(build_dir, photo, state)


def build_all_photo_assets(context: BuildContext) -> None:
    logger.info('Building photo assets')
    # Parallelising this as reencoding images is quite slow.
    with ThreadPool() as pool:
        pool.map(
            lambda photo: build_photo_assets(context.build_dir, photo, context.state),
            context.photos)
