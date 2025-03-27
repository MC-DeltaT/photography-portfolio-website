from buildtool.types import PhotoID, URLPath


# TODO: remove .html, it's just for testing


INDEX_PAGE_URL = URLPath('/index.html')

ABOUT_PAGE_URL = URLPath('/about.html')

GALLERY_URL = URLPath('/gallery')
GALLERY_BY_STYLE_URL = GALLERY_URL / 'style'
GALLERY_BY_STYLE_PAGE_URL = GALLERY_BY_STYLE_URL.with_suffix('.html')
GALLERY_BY_DATE_URL = GALLERY_URL / 'date'
GALLERY_BY_DATE_PAGE_URL = GALLERY_BY_DATE_URL.with_suffix('.html')
GALLERY_PHOTO_URL = GALLERY_URL / 'photo'


def get_gallery_style_page_url(style: str) -> URLPath:
    return GALLERY_BY_STYLE_URL / f'{style.lower()}.html'


def get_single_photo_page_url(photo_id: PhotoID) -> URLPath:
    return GALLERY_PHOTO_URL / f'{photo_id}.html'


ASSETS_URL = URLPath('/asset')
ASSETS_IMAGE_URL = ASSETS_URL / 'image'
ASSETS_IMAGE_GENERAL_URL = ASSETS_IMAGE_URL / 'general'
ASSETS_IMAGE_PHOTO_URL = ASSETS_IMAGE_URL / 'photo'


def create_image_srcset_url(base_url: URLPath, srcset_tag: str | None) -> URLPath:
    """Takes the URL for the original image and creates a URL for a srcset entry."""

    if srcset_tag is None:
        return base_url
    else:
        # Add the srcset tag to the end of the name
        parts = base_url.name.split('.')
        parts[0] += f'-{srcset_tag}'
        name = '.'.join(parts)
        url = base_url.with_name(name)
        return url


def get_photo_asset_base_url(photo_id: PhotoID, file_extension: str) -> URLPath:
    """URL for the original image. Can be modified further by create_image_srcset_url() to create a srcset."""

    assert file_extension.startswith('.')
    name_part = f'{photo_id}{file_extension}'
    return ASSETS_IMAGE_PHOTO_URL / name_part


ASSETS_CSS_URL = ASSETS_URL / 'css'


def get_css_asset_url(filename: str) -> URLPath:
    return ASSETS_CSS_URL / filename
