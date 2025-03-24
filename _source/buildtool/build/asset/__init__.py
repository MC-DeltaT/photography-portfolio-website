from ..common import BuildContext
from .photo import build_photo_assets


def build_assets(context: BuildContext) -> None:
    build_photo_assets(context)
