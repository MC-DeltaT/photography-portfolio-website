import logging

from buildtool.build.common import BuildContext
from buildtool.resource.js import get_js_resources
from buildtool.url import ASSETS_JS_URL

from rjsmin import jsmin


logger = logging.getLogger(__name__)


def build_all_js_assets(context: BuildContext) -> None:
    logger.info('Building JS assets')
    for full_path, relative_path in get_js_resources(context.resources_path):
        url = ASSETS_JS_URL / relative_path
        content = full_path.read_text(encoding='utf-8')
        minified = jsmin(content)
        context.build_dir.build_content(minified, url)
