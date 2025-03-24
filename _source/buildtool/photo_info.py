from dataclasses import dataclass
from pathlib import Path

from .genre import PhotoGenre
from .image import open_image_file, read_image_metadata
from .resource.photo import PhotoResourceRecord, PhotoMetadataFile
from .types import ISO, Aperture, ExposureTime, FocalLength, PartialDate, PartialDateStr, PhotoUniqueId


@dataclass(frozen=True)
class PhotoInfo:
    source_path: Path
    unique_id: PhotoUniqueId
    file_extension: str     # Includes the .
    name: str
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


def create_photo_unique_id(name: str, date: PartialDate) -> PhotoUniqueId:
    date_str = str(date)
    if date_str:
        s = f'{date}-{name}'
    else:
        # Totally unknown date.
        # TODO: should we use some placeholder for the date?
        s = name
    return PhotoUniqueId(s)


def get_photo_name(source_path: Path) -> str:
    return source_path.name.split('.')[0]


def resolve_photo_date(user_date: PartialDateStr | None) -> PartialDate:
    # TODO: look at exif data
    # TODO: how does date get parsed from json by pydantic?
    if user_date is None:
        return PartialDate.from_str('')
        raise NotImplementedError()
    return PartialDate.from_str(user_date)


def read_photo_info(resource: PhotoResourceRecord) -> PhotoInfo:
    """Creates final information about a photo by combining the image file metadata and user specified metadata."""

    user_metadata = PhotoMetadataFile.from_file(resource.metadata_file_path)

    image_metadata = read_image_metadata(open_image_file(resource.image_file_path))

    file_extension = resource.image_file_path.suffix
    name = get_photo_name(resource.image_file_path)
    date = resolve_photo_date(user_metadata.date)
    camera_model = user_metadata.camera_model or image_metadata.camera_model
    lens_model = user_metadata.lens_model or image_metadata.lens_model
    focal_length = user_metadata.focal_length or image_metadata.focal_length
    aperture = user_metadata.aperture or image_metadata.aperture
    exposure_time = user_metadata.exposure_time or image_metadata.exposure_time
    iso = user_metadata.iso or image_metadata.iso

    return PhotoInfo(
        source_path=resource.image_file_path,
        unique_id=create_photo_unique_id(name, date),
        file_extension=file_extension,
        name=name,
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
        genre=user_metadata.genre
    )
