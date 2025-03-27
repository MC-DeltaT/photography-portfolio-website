import logging

from buildtool.build.asset.image.common import build_image_srcset_assets
from buildtool.build.common import BuildContext
from buildtool.resource.image import get_general_image_resources
from buildtool.types import ImageSrcSet
from buildtool.url import ASSETS_IMAGE_GENERAL_URL


logger = logging.getLogger(__name__)


def build_all_general_image_assets(context: BuildContext) -> None:
    logger.info('Building general image assets')

    for full_path, relative_path in get_general_image_resources(context.resources_path):
        base_url = ASSETS_IMAGE_GENERAL_URL / relative_path
        srcset_entries = build_image_srcset_assets(context.build_dir, full_path, base_url)
        # Save the resulting srcset assets for later when embedding URLs in pages,
        # since other it's not easy to know what image sizes we computed here.
        context.state.image_srcsets[image_id] = ImageSrcSet(tuple(srcset_entries), default_index=0)
