from .types import PhotoUniqueID, URLPath


# TODO: remove .html, it's just for testing


INDEX_PAGE_URL = URLPath('/index.html')

ABOUT_PAGE_URL = URLPath('/about.html')

GALLERY_URL = URLPath('/gallery')
GALLERY_BY_STYLE_URL = GALLERY_URL / 'style'
GALLERY_BY_STYLE_PAGE_URL = GALLERY_BY_STYLE_URL.with_suffix('.html')
GALLERY_BY_DATE_URL = GALLERY_URL / 'date'
GALLERY_BY_DATE_PAGE_URL = GALLERY_BY_DATE_URL.with_suffix('.html')
PHOTO_PAGE_URL = GALLERY_URL / 'photo'


def get_gallery_style_page_url(style: str) -> URLPath:
    return GALLERY_BY_STYLE_URL / f'{style.lower()}.html'


def get_single_photo_page_url(unique_id: PhotoUniqueID) -> URLPath:
    return PHOTO_PAGE_URL / f'{unique_id}.html'


ASSETS_URL = URLPath('/assets')

PHOTO_ASSETS_URL = ASSETS_URL / 'photo'


def get_photo_asset_url(unique_id: PhotoUniqueID, file_extension: str, srcset_tag: str | None) -> URLPath:
    assert file_extension.startswith('.')
    srcset_part = f'-{srcset_tag}' if srcset_tag else ''
    name_part = f'{unique_id}{srcset_part}{file_extension}'
    return PHOTO_ASSETS_URL / name_part


CSS_ASSETS_URL = ASSETS_URL / 'css'


def get_css_asset_url(filename: str) -> URLPath:
    return CSS_ASSETS_URL / filename
