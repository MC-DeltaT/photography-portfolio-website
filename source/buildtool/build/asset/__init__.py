import logging

from buildtool.build.asset.css import build_all_css_assets
from buildtool.build.asset.image import build_all_image_assets
from buildtool.build.asset.js import build_all_js_assets
from buildtool.build.common import BuildContext

logger = logging.getLogger(__name__)


def build_all_assets(context: BuildContext) -> None:
    logger.info('Building assets')
    build_all_css_assets(context)
    build_all_js_assets(context)
    build_all_image_assets(context)
