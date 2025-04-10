from dataclasses import dataclass
import datetime as dt
from pathlib import Path
import logging

from buildtool.image import open_image_file, read_image_exif_metadata
from buildtool.resource.photo import PhotoResourceRecord, PhotoMetadataFile
from buildtool.types import ISO, Aperture, ExposureTime, FocalLength, PartialDate, PhotoGenre, PhotoID, Size
from buildtool.utility import remove_dashes


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PhotoInfo:
    source_path: Path
    id: PhotoID
    file_extension: str     # Includes the .
    date: PartialDate
    title: str | None
    description: str | None
    location: str | None
    camera_model: str | None
    lens_model: str | None
    focal_length: FocalLength | None
    aperture: Aperture | None
    exposure_time: ExposureTime | None
    iso: ISO | None
    genre: tuple[PhotoGenre, ...]
    size_px: Size

    @property
    def chronological_sort_key(self):
        # Sort by date, then by ID to break ties consistently.
        return self.date.to_str(unknown_placeholder='0'), self.id


def create_photo_id(name: str, date: PartialDate, file_extension: str) -> PhotoID:
    # Only allow alphabetic and number characters to simplify and prevent messing with URL encoding.
    # Allows dashes because they're common, but remove them.
    name = remove_dashes(name)
    if not name:
        raise ValueError('Photo name must not be empty')
    if not (name.isalnum() and name.isascii()):
        raise ValueError('Photo name must be alphanumeric')
    date_str = date.to_str(separator='', unknown_placeholder='x')
    s = f'{date_str}-{name}'
    assert file_extension.startswith('.')
    s += file_extension
    return PhotoID(s)


def get_photo_name(source_path: Path) -> str:
    return source_path.name.split('.')[0].lower()


def resolve_photo_date(image_date: dt.date | None, user_date: PartialDate | None) -> PartialDate:
    # TODO: take into account timezone
    if user_date:
        return user_date
    elif image_date is None:
        raise RuntimeError('Photo has no date in image metadata, you must specify it!')
    else:
        return PartialDate.from_date(image_date)


def read_photo_info(resource: PhotoResourceRecord) -> PhotoInfo:
    """Creates final information about a photo by combining the image file metadata and user specified metadata."""

    logger.info(f'Reading photo info: {resource}')

    user_metadata = PhotoMetadataFile.from_file(resource.metadata_file_path)

    image = open_image_file(resource.image_file_path)
    image_metadata = read_image_exif_metadata(image)

    # Normalise to lowercase so file names and URLs are consistent.
    file_extension = resource.image_file_path.suffix.lower()
    name = get_photo_name(resource.image_file_path)
    date = resolve_photo_date(image_metadata.date_time_original, user_metadata.date)
    if not date:
        raise RuntimeError(f'Photo with unknown date: {resource}')
    id_ = create_photo_id(name, date, file_extension)
    camera_model = user_metadata.camera_model or image_metadata.camera_model
    lens_model = user_metadata.lens_model or image_metadata.lens_model
    focal_length = user_metadata.focal_length or image_metadata.focal_length
    aperture = user_metadata.aperture or image_metadata.aperture
    exposure_time = user_metadata.exposure_time or image_metadata.exposure_time
    iso = user_metadata.iso or image_metadata.iso
    size_px = Size((image.width, image.height))

    return PhotoInfo(
        source_path=resource.image_file_path,
        id=id_,
        file_extension=file_extension,
        date=date,
        title=user_metadata.title,
        description=user_metadata.description,
        location=user_metadata.location,
        camera_model=camera_model,
        lens_model=lens_model,
        focal_length=focal_length,
        aperture=aperture,
        exposure_time=exposure_time,
        iso=iso,
        genre=user_metadata.genre,
        size_px=size_px
    )
