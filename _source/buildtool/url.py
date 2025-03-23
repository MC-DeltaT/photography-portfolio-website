from .types import PhotoUniqueId


PHOTO_PAGE_URL = '/photo'


def get_single_photo_page_url(unique_id: PhotoUniqueId) -> str:
    return f'{PHOTO_PAGE_URL}/{unique_id}'


ASSETS_URL = '/assets'

PHOTO_ASSET_URL = f'{ASSETS_URL}/photo'


def get_photo_asset_url(unique_id: PhotoUniqueId) -> str:
    return f'{PHOTO_ASSET_URL}/{unique_id}'
