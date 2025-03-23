from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import logging

import pydantic

from ..genre import PhotoGenre
from ..types import Aperture, CaptureDateStr, FocalLength, ISO, ShutterSpeed


logger = logging.getLogger(__name__)


def get_photo_resource_path(resources_path: Path) -> Path:
    return resources_path / 'images'


SUPPORTED_IMAGE_EXTENSIONS = (
    '.jpeg',
    '.jpg',
    '.png'
)


@dataclass(frozen=True)
class PhotoResourceRecord:
    image_file_path: Path
    metadata_file_path: Path


METADATA_FILE_EXTENSION = '.json'


def get_image_files(dir_path: Path, file_names: Iterable[str]) -> list[Path]:
    return [
        dir_path / f for f in file_names
        if any(f.lower().endswith(e) for e in SUPPORTED_IMAGE_EXTENSIONS)]


def get_photo_metadata_files(dir_path: Path, file_names: Iterable[str]) -> list[Path]:
    return [dir_path / f for f in file_names if f.lower().endswith(METADATA_FILE_EXTENSION)]


def image_file_from_metadata_file(metadata_file: Path) -> Path:
    """Computes the expected image file name from the metadata file name."""

    # Image file: IMG1234.jpg
    # Metadata file: IMG1234.jpg.json
    return metadata_file.with_suffix('')


def find_photos(root: Path) -> list[PhotoResourceRecord]:
    """Finds all photos within the directory."""

    logger.info(f'Finding photos in: "{root}"')
    records: list[PhotoResourceRecord] = []
    for dir_path, _subdirs, files in root.walk():
        files = sorted(files)
        metadata_files = get_photo_metadata_files(dir_path, files)
        logger.debug(f'Metadata files in "{dir_path}" : {metadata_files}')
        image_files = get_image_files(dir_path, files)
        logger.debug(f'Image files in "{dir_path}" : {image_files}')
        expected_image_files = [image_file_from_metadata_file(f) for f in metadata_files]
        logger.debug(f'Expected image files in "{dir_path}" : {expected_image_files}')

        for f in image_files:
            if f not in expected_image_files:
                raise RuntimeError(f'Image file with no metadata file: {f}')

        for metadata_file, image_file in zip(metadata_files, expected_image_files):
            logger.debug(f'Resolved metadata file to image file: "{metadata_file}" -> "{image_file}"')
            if not image_file.exists():
                raise RuntimeError(f'Metadata file with no image file: "{metadata_file}"')
            if not image_file.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                raise RuntimeError(f'Unsupported image format: "{image_file}"')
            record = PhotoResourceRecord(image_file, metadata_file)
            records.append(record)
    return records


class PhotoMetadataFile(pydantic.BaseModel, frozen=True):
    """Model class for the photo metadata JSON file."""

    capture_date: CaptureDateStr | None = None
    """Local time when the photo was taken. If None, infer from the image file."""

    title: str | None = pydantic.Field(default=None, min_length=1)
    """Main name of the photo. Optional."""

    description: str | None = pydantic.Field(default=None, min_length=1)
    """General purpose text accompanying the photo."""

    location: str | None = pydantic.Field(default=None, min_length=1)
    """Place the photo was taken. Optional."""

    set: str | None = pydantic.Field(default=None, min_length=1)
    """Event, occasion, or other collection the photo is part of. Optional."""

    camera_model: str | None = pydantic.Field(default=None, min_length=1)
    """Camera model name. If None, infer from the image file."""

    lens_model: str | None = pydantic.Field(default=None, min_length=1)
    """Lens model name. If None, infer from the image file."""

    focal_length: FocalLength | None = pydantic.Field(default=None, gt=0)
    """Lens focal length. If None, infer from the image file."""

    aperture: Aperture | None = pydantic.Field(default=None, gt=0)
    """Aperture. If None, infer from the image file."""

    shutter_speed: ShutterSpeed | None = None
    """Shutter speed. If None, infer from the image file."""

    iso: ISO | None = pydantic.Field(default=None, gt=0)
    """ISO. If None, infer from the image file."""

    genre: tuple[PhotoGenre, ...] = pydantic.Field(min_length=1)
    """Genres applicable to this photo."""

    @classmethod
    def from_file(cls, path: Path):
        logger.debug(f'Loading photo metadata file: "{path}"')
        with open(path, 'r', encoding='utf8') as f:
            json_data = f.read()
        return cls.model_validate_json(json_data, strict=True)
