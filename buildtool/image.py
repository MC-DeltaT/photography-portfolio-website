import datetime as dt
import logging
from pathlib import Path
import subprocess
from typing import Annotated

from PIL import ExifTags
from PIL.Image import Image, open as pil_image_open
import pydantic

from buildtool.types import Aperture, ExposureTime, FocalLength, ISO, CoerceNumber
from buildtool.utility import parse_datetime

logger = logging.getLogger(__name__)


def open_image_file(path: Path) -> Image:
    return pil_image_open(path)


class EXIFMetadata(pydantic.BaseModel, frozen=True):
    # # "The date and time of image creation. In Exif standard, it is the date and time the file was changed."
    # date_time: str | None
    # "The date and time when the original image data was generated."
    date_time_original: Annotated[dt.datetime, pydantic.BeforeValidator(parse_datetime)] | None
    # # "The date and time when the image was stored as digital data."
    # date_time_digitised: str | None
    # offset_time: str | None
    # offset_time_original: str | None
    # offset_time_digitised: str | None
    camera_model: str | None
    lens_model: str | None
    # Note EXIF data uses a custom type for some numbers,
    # which needs to be coerced to a built-in type to work with Pydantic.
    focal_length: CoerceNumber[FocalLength] | None
    aperture: CoerceNumber[Aperture] | None
    exposure_time: CoerceNumber[ExposureTime] | None
    iso: CoerceNumber[ISO] | None


def read_image_exif_metadata(image: Image) -> EXIFMetadata:
    exif = image.getexif()
    ifd_exif = exif.get_ifd(ExifTags.IFD.Exif)

    metadata = EXIFMetadata(
        # date_time=exif.get(ExifTags.Base.DateTime),
        date_time_original=ifd_exif.get(ExifTags.Base.DateTimeOriginal),
        # date_time_digitised=ifd_exif.get(ExifTags.Base.DateTimeDigitized),
        # offset_time=ifd_exif.get(ExifTags.Base.OffsetTime),
        # offset_time_original=ifd_exif.get(ExifTags.Base.OffsetTimeOriginal),
        # offset_time_digitised=ifd_exif.get(ExifTags.Base.OffsetTimeDigitized),
        camera_model=exif.get(ExifTags.Base.Model),
        lens_model=ifd_exif.get(ExifTags.Base.LensModel),
        focal_length=ifd_exif.get(ExifTags.Base.FocalLength),
        aperture=ifd_exif.get(ExifTags.Base.FNumber),
        exposure_time=ifd_exif.get(ExifTags.Base.ExposureTime),
        iso=ifd_exif.get(ExifTags.Base.ISOSpeedRatings),
    )
    logger.debug(f"Read image file metadata: {metadata}")
    return metadata


def reencode_image(input_file: Path, output_file: Path, max_width: int | None, max_height: int | None, quality: int,
        fast: bool = False) -> None:
    if output_file.suffix != '.jpg':
        # We only deal with JPGs, so probably wrong to try to output anything else.
        raise ValueError('Only JPG output is supported')
    # We could do this with a Python library, but I only trust ImageMagick to pass through the metadata correctly.
    operation = '-scale' if fast else '-resize'
    if max_width and max_height:
        size_str = f'{max_width}x{max_height}'
    elif max_width:
        size_str = f'{max_width}x'
    elif max_height:
        size_str = f'x{max_height}'
    else:
        raise ValueError('Either max_width or max_height must be specified')
    args = [
        'magick', str(input_file),
        operation, size_str,
        '-quality', str(quality),
        str(output_file)
    ]
    logger.debug(f'> {args}')
    subprocess.run(args, check=True)
    if not output_file.is_file():
        raise RuntimeError('Reencoding failed')


def strip_image_exif_gps(file: Path) -> None:
    """Remove all GPS EXIF tags from an image in place.
        Reason is to avoid people stalking us from photo content."""

    # We could do this with a Python library, but I only trust ExifTool to do it correctly.
    args = ['exiftool', '-gps*=', str(file)]
    logger.debug(f'> {args}')
    subprocess.run(args, check=True)
