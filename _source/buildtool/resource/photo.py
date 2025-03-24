from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import logging
from typing import Annotated

import pydantic

from ..genre import PhotoGenre
from ..types import Aperture, ExposureTime, FocalLength, ISO, NonEmptyStr, PartialDate


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

    # TODO: allow setting field to null in json which stops infer from image

    # TODO: specify timezone somehow

    date: Annotated[PartialDate, pydantic.BeforeValidator(PartialDate.from_str)] | None = None
    """Local time when the photo was taken. If None, infer from the image file."""

    title: NonEmptyStr | None = None
    """Main name of the photo. Optional."""

    description: NonEmptyStr | None = None
    """General purpose text accompanying the photo."""

    location: NonEmptyStr | None = None
    """Place the photo was taken. Optional."""

    set: NonEmptyStr | None = None
    """Event, occasion, or other collection the photo is part of. Optional."""

    camera_model: NonEmptyStr | None = None
    """Camera model name. If None, infer from the image file."""

    lens_model: NonEmptyStr | None = None
    """Lens model name. If None, infer from the image file."""

    focal_length: FocalLength | None = None
    """Lens focal length. If None, infer from the image file."""

    aperture: Aperture | None = None
    """Aperture. If None, infer from the image file."""

    # TODO: allow format like 1/100
    exposure_time: ExposureTime | None = None
    """Exposure duration in seconds (inverse of shutter speed). If None, infer from the image file."""

    iso: ISO | None = None
    """ISO. If None, infer from the image file."""

    genre: tuple[PhotoGenre, ...] = pydantic.Field(min_length=1)
    """Genres applicable to this photo."""

    @classmethod
    def from_file(cls, path: Path):
        logger.debug(f'Reading photo metadata file: "{path}"')
        with open(path, 'r', encoding='utf8') as f:
            json_data = f.read()
        obj = cls.model_validate_json(json_data, strict=True)
        logger.debug(f'Read photo metadata file: {obj}')
        return obj
