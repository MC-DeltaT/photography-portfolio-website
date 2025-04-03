import logging

from buildtool.build.common import BuildContext
from buildtool.resource.js import get_js_resources
from buildtool.url import ASSETS_JS_URL


logger = logging.getLogger(__name__)


def build_all_js_assets(context: BuildContext) -> None:
    logger.info('Building JS assets')
    for full_path, relative_path in get_js_resources(context.resources_path):
        url = ASSETS_JS_URL / relative_path
        context.build_dir.build_file(full_path, url)
