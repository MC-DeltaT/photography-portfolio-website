import datetime as dt


def get_photo_id(date: dt.date, name: str) -> str:
    """Globally unique identifier for a photo."""

    if '.' in name:
        # Purposely not including the file extension into the URL because it's more on an implementation detail.
        raise ValueError('Photo name should not contain extension')
    date_str = date.strftime('%Y%m%d')
    return f'{date_str}-{name}'


PHOTO_PAGE_URL = '/photo'


def get_single_photo_page_url(date: dt.date, name: str) -> str:
    if '.' in name:
        # Purposely not including the file extension into the URL because it's more on an implementation detail.
        raise ValueError('Photo name should not contain extension')
    return f'{PHOTO_PAGE_URL}/{get_photo_id(date, name)}'


ASSETS_URL = '/assets'

PHOTO_ASSET_URL = f'{ASSETS_URL}/photo'


def get_photo_asset_url(date: dt.date, name: str) -> str:
    return f'{PHOTO_ASSET_URL}/{get_photo_id(date, name)}'
