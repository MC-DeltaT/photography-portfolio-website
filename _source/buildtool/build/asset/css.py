import logging
import shutil

from buildtool.build.common import BuildContext
from buildtool.resource.css import get_css_resources_path
from buildtool.url import ASSETS_CSS_URL


logger = logging.getLogger(__name__)


def build_all_css_assets(context: BuildContext) -> None:
    source_path = get_css_resources_path(context.resources_path)
    url = ASSETS_CSS_URL
    logger.info(f'Building CSS assets URL: {url}')
    dest_path = context.build_dir.prepare_directory(url.fs_path)
    logger.debug(f'Copying CSS files: "{source_path}" -> "{dest_path}"')
    if not context.dry_run:
        shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
