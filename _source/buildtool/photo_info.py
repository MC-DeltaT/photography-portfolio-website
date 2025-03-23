from dataclasses import dataclass
from pathlib import Path

from .genre import PhotoGenre
from .resource.photo import PhotoResourceRecord, PhotoMetadataFile
from .types import ISO, Aperture, FocalLength, PartialDate, PartialDateStr, PhotoUniqueId, ShutterSpeed


@dataclass(frozen=True)
class PhotoInfo:
    source_path: Path
    unique_id: PhotoUniqueId
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
    shutter_speed: ShutterSpeed | None
    iso: ISO | None
    genre: tuple[PhotoGenre, ...]


def create_photo_unique_id(name: str, date: PartialDate) -> PhotoUniqueId:
    return PhotoUniqueId(f'{date}-{name}')


def get_photo_name(source_path: Path) -> str:
    return source_path.name.split('.')[0]


def resolve_photo_date(metadata_date: PartialDateStr | None) -> PartialDate:
    # TODO: look at exif data
    # TODO: how does date get parsed from json by pydantic?
    print(type(metadata_date), metadata_date)
    if metadata_date is None:
        raise NotImplementedError()
    return PartialDate.from_str(metadata_date)


def resolve_photo_camera_model(metadata_camera_model: str | None) -> str | None:
    # TODO: look at exif data
    return metadata_camera_model


def resolve_photo_lens_model(metadata_lens_model: str | None) -> str | None:
    # TODO: look at exif data
    return metadata_lens_model


def resolve_photo_focal_length(metadata_focal_length: FocalLength | None) -> FocalLength | None:
    # TODO: look at exif data
    return metadata_focal_length


def resolve_photo_aperture(metadata_aperture: Aperture | None) -> Aperture | None:
    # TODO: look at exif data
    return metadata_aperture


def resolve_photo_shutter_speed(metadata_shutter_speed: ShutterSpeed | None) -> ShutterSpeed | None:
    # TODO: look at exif data
    return metadata_shutter_speed


def resolve_photo_iso(metadata_iso: ISO | None) -> ISO | None:
    # TODO: look at exif data
    return metadata_iso


def read_photo_info(resource: PhotoResourceRecord) -> PhotoInfo:
    """Creates final information about a photo by combining the image file metadata and user specified metadata."""

    metadata = PhotoMetadataFile.from_file(resource.metadata_file_path)

    name = get_photo_name(resource.image_file_path)
    date = resolve_photo_date(metadata.date)

    return PhotoInfo(
        source_path=resource.image_file_path,
        unique_id=create_photo_unique_id(name, date),
        name=name,
        date=date,
        title=metadata.title,
        description=metadata.description,
        location=metadata.location,
        set=metadata.set,
        camera_model=resolve_photo_camera_model(metadata.camera_model),
        lens_model=resolve_photo_lens_model(metadata.lens_model),
        focal_length=resolve_photo_focal_length(metadata.focal_length),
        aperture=resolve_photo_aperture(metadata.aperture),
        shutter_speed=resolve_photo_shutter_speed(metadata.shutter_speed),
        iso=resolve_photo_iso(metadata.iso),
        genre=metadata.genre
    )
