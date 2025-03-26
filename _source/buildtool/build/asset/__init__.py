from buildtool.build.asset.css import build_all_css_assets
from buildtool.build.asset.image import build_all_image_assets
from buildtool.build.common import BuildContext


def build_all_assets(context: BuildContext) -> None:
    build_all_image_assets(context)
    build_all_css_assets(context)
