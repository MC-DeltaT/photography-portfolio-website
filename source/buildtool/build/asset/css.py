import logging

from buildtool.build.common import BuildContext
from buildtool.resource.css import get_css_resources
from buildtool.url import ASSETS_CSS_URL


logger = logging.getLogger(__name__)


def build_all_css_assets(context: BuildContext) -> None:
    logger.info('Building CSS assets')
    for full_path, relative_path in get_css_resources(context.resources_path):
        url = ASSETS_CSS_URL / relative_path
        context.build_dir.build_file(full_path, url)
