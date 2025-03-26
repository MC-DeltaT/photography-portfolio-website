from buildtool.build.asset.image.general import build_all_general_image_assets
from buildtool.build.asset.image.photo import build_all_photo_assets
from buildtool.build.common import BuildContext


def build_all_image_assets(context: BuildContext) -> None:
    build_all_general_image_assets(context)
    build_all_photo_assets(context)
