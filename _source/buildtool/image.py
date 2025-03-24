import logging
from pathlib import Path

from PIL import ExifTags
from PIL.Image import Image, open as pil_image_open
import pydantic

from .types import Aperture, ExposureTime, FocalLength, ISO, CoerceNumber


logger = logging.getLogger(__name__)


def open_image_file(path: Path) -> Image:
    return pil_image_open(path)


class EXIFMetadata(pydantic.BaseModel, frozen=True):
    camera_model: str | None
    lens_model: str | None
    # Note EXIF data uses a custom type for some numbers,
    # which needs to be coerced to a built-in type to work with Pydantic.
    focal_length: CoerceNumber[FocalLength] | None  # mm
    aperture: CoerceNumber[Aperture] | None
    exposure_time: CoerceNumber[ExposureTime] | None  # seconds
    iso: CoerceNumber[ISO] | None


def read_image_metadata(image: Image) -> EXIFMetadata:
    exif = image.getexif()
    ifd_exif = exif.get_ifd(ExifTags.IFD.Exif)

    metadata = EXIFMetadata(
        camera_model=exif.get(ExifTags.Base.Model),
        lens_model=ifd_exif.get(ExifTags.Base.LensModel),
        focal_length=ifd_exif.get(ExifTags.Base.FocalLength),
        aperture=ifd_exif.get(ExifTags.Base.FNumber),
        exposure_time=ifd_exif.get(ExifTags.Base.ExposureTime),
        iso=ifd_exif.get(ExifTags.Base.ISOSpeedRatings),
    )
    logger.debug(f"Read image file metadata: {metadata}")
    return metadata
