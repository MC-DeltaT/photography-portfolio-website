from ..common import BuildContext
from .css import build_all_css_assets
from .photo import build_all_photo_assets


def build_all_assets(context: BuildContext) -> None:
    build_all_photo_assets(context)
    build_all_css_assets(context)
