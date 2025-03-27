import logging

from buildtool.build.common import BuildContext
from buildtool.resource.css import get_css_resources_path
from buildtool.url import ASSETS_CSS_URL
from buildtool.utility import find_files


logger = logging.getLogger(__name__)


def build_all_css_assets(context: BuildContext) -> None:
    logger.info('Building CSS assets')
    resources_path = get_css_resources_path(context.resources_path)
    for file in find_files(resources_path, ('.css',)):
        url = ASSETS_CSS_URL / file.relative_to(resources_path)
        context.build_dir.build_file(file, url)
