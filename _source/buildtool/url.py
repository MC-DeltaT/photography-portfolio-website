from pathlib import Path, PurePosixPath

from .types import PhotoUniqueId


class URLPath(PurePosixPath):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not self.is_absolute():
            raise ValueError('path must have a root')

    @property
    def fs_path(self) -> Path:
        return Path(*self.parts[1:])


PHOTO_PAGE_URL = URLPath('/photo')


def get_single_photo_page_url(unique_id: PhotoUniqueId) -> URLPath:
    return PHOTO_PAGE_URL / unique_id


ASSETS_URL = URLPath('/assets')

PHOTO_ASSETS_URL = ASSETS_URL / 'photo'


def get_photo_asset_url(unique_id: PhotoUniqueId, file_extension: str) -> URLPath:
    name_part = str(unique_id) + file_extension
    return PHOTO_ASSETS_URL / name_part


CSS_ASSETS_URL = ASSETS_URL / 'css'
