from dataclasses import dataclass
import datetime as dt
from pathlib import Path
import logging

from .genre import PhotoGenre
from .image import open_image_file, read_image_exif_metadata
from .resource.photo import PhotoResourceRecord, PhotoMetadataFile
from .types import ISO, Aperture, ExposureTime, FocalLength, PartialDate, PhotoUniqueId, Size


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PhotoInfo:
    source_path: Path
    unique_id: PhotoUniqueId
    file_extension: str     # Includes the .
    date: PartialDate
    title: str | None
    description: str | None
    location: str | None
    set: str | None
    camera_model: str | None
    lens_model: str | None
    focal_length: FocalLength | None
    aperture: Aperture | None
    exposure_time: ExposureTime | None
    iso: ISO | None
    genre: tuple[PhotoGenre, ...]
    size_px: Size


def create_photo_unique_id(name: str, date: PartialDate) -> PhotoUniqueId:
    date_str = date.to_str(separator='')
    if date_str:
        s = f'{date_str}-{name}'
    else:
        # Totally unknown date.
        # TODO: should we use some placeholder for the date?
        s = name
    return PhotoUniqueId(s)


def get_photo_name(source_path: Path) -> str:
    return source_path.name.split('.')[0].lower()


def resolve_photo_date(image_date: dt.date, user_date: PartialDate | None) -> PartialDate:
    # TODO: take into account timezone
    if user_date:
        return user_date
    else:
        return PartialDate.from_date(image_date)


def read_photo_info(resource: PhotoResourceRecord) -> PhotoInfo:
    """Creates final information about a photo by combining the image file metadata and user specified metadata."""

    logger.debug(f'Reading photo info: {resource}')

    user_metadata = PhotoMetadataFile.from_file(resource.metadata_file_path)

    image = open_image_file(resource.image_file_path)
    image_metadata = read_image_exif_metadata(image)

    file_extension = resource.image_file_path.suffix
    name = get_photo_name(resource.image_file_path)
    date = resolve_photo_date(image_metadata.date_time_original, user_metadata.date)
    unique_id = create_photo_unique_id(name, date)
    camera_model = user_metadata.camera_model or image_metadata.camera_model
    lens_model = user_metadata.lens_model or image_metadata.lens_model
    focal_length = user_metadata.focal_length or image_metadata.focal_length
    aperture = user_metadata.aperture or image_metadata.aperture
    exposure_time = user_metadata.exposure_time or image_metadata.exposure_time
    iso = user_metadata.iso or image_metadata.iso
    size_px = Size((image.width, image.height))

    return PhotoInfo(
        source_path=resource.image_file_path,
        unique_id=unique_id,
        file_extension=file_extension,
        date=date,
        title=user_metadata.title,
        description=user_metadata.description,
        location=user_metadata.location,
        set=user_metadata.set,
        camera_model=camera_model,
        lens_model=lens_model,
        focal_length=focal_length,
        aperture=aperture,
        exposure_time=exposure_time,
        iso=iso,
        genre=user_metadata.genre,
        size_px=size_px
    )
