from pathlib import PurePosixPath

from buildtool.types import ImageID, PhotoID, URLPath


# TODO: remove .html, it's just for testing


INDEX_PAGE_URL = URLPath('/index.html')

ABOUT_PAGE_URL = URLPath('/about.html')

GALLERY_URL = URLPath('/gallery')
GALLERY_PAGE_URL = GALLERY_URL.with_suffix('.html')
GALLERY_BY_STYLE_URL = GALLERY_URL / 'style'
GALLERY_PHOTO_URL = GALLERY_URL / 'photo'


def get_gallery_style_page_url(style: str) -> URLPath:
    return GALLERY_BY_STYLE_URL / f'{style.lower()}.html'


def get_single_photo_page_url(photo_id: PhotoID) -> URLPath:
    name_part, _ = photo_id.split('.')
    return GALLERY_PHOTO_URL / f'{name_part}.html'


ASSETS_URL = URLPath('/asset')
ASSETS_IMAGE_URL = ASSETS_URL / 'image'
PHOTO_IMAGE_DIR = 'photo'


def get_image_base_url(image_id: ImageID) -> URLPath:
    relative_path = PurePosixPath(image_id)
    assert not relative_path.is_absolute()
    return ASSETS_IMAGE_URL / relative_path


def get_image_srcset_url(base_url: URLPath, srcset_tag: str | None) -> URLPath:
    """Takes the URL for the original image and creates a URL for a srcset entry."""

    if srcset_tag is None:
        return base_url
    else:
        assert srcset_tag.isalnum()
        # Add the srcset tag to the end of the name
        parts = base_url.name.split('.')
        parts[0] += f'-{srcset_tag}'
        name = '.'.join(parts)
        url = base_url.with_name(name)
        return url


ASSETS_CSS_URL = ASSETS_URL / 'css'
