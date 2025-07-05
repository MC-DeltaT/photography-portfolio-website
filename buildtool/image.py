from collections.abc import Sequence
from dataclasses import dataclass
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


@dataclass(frozen=True)
class ImageReencodingArgs:
    output_file: Path
    max_width: int | None
    max_height: int | None
    quality: int
    fast: bool = False
    input_label: str | None = None
    output_label: str | None = None


def reencode_image(input_file: Path, args: ImageReencodingArgs | Sequence[ImageReencodingArgs]) -> None:
    # We could do this with a Python library, but I only trust ImageMagick to pass through the metadata correctly.

    def get_operation(args: ImageReencodingArgs) -> str:
        if args.fast:
            return '-scale'
        else:
            return '-resize'

    def get_size_spec(args: ImageReencodingArgs) -> str:
        if args.max_width and args.max_height:
            return f'{args.max_width}x{args.max_height}'
        elif args.max_width:
            return f'{args.max_width}x'
        elif args.max_height:
            return f'x{args.max_height}'
        else:
            raise ValueError('Either max_width or max_height must be specified')

    INPUT_MPR = 'input'

    def get_magick_args(args: ImageReencodingArgs, first: bool, last: bool) -> list[str]:
        magick_args: list[str] = []
        if first:
            if args.input_label:
                raise ValueError('First reencoding cannot have input_label')
        else:
            magick_args.append(f'mpr:{args.input_label or INPUT_MPR}')
        magick_args += [
            get_operation(args), get_size_spec(args),
            '-quality', str(args.quality)
        ]
        if not last:
            magick_args.append('-write')
        magick_args.append(str(args.output_file))
        if not last:
            if args.output_label:
                magick_args += ['-write', f'mpr:{args.output_label}']
            magick_args.append('+delete')
        return magick_args

    if isinstance(args, ImageReencodingArgs):
        args_list = (args,)
    else:
        if len(args) == 0:
            raise ValueError('args must not be an empty sequence')
        args_list = args

    if not all(args.output_file.suffix == '.jpg' for args in args_list):
        # We only deal with JPGs, so probably wrong to try to output anything else.
        raise ValueError('Only JPG output is supported')
    if len({args.output_file for args in args_list}) != len(args_list):
        raise ValueError('Output files must be unique')

    # We could do this with a Python library, but I only trust ImageMagick to pass through the metadata correctly.

    proc_args = [
        'magick', str(input_file),
    ]
    if len(args_list) > 1:
        proc_args += ['-write', f'mpr:{INPUT_MPR}']
    for i, args in enumerate(args_list):
        proc_args += get_magick_args(args, i == 0, i == len(args_list) - 1)
    logger.debug(f'> {proc_args}')
    subprocess.run(proc_args, check=True, text=True)

    if not all(args.output_file.is_file() for args in args_list):
        raise RuntimeError('Reencoding failed')


def strip_image_exif_gps(file: Path) -> None:
    """Remove all GPS EXIF tags from an image in place.
        Reason is to avoid people stalking us from photo content."""

    # We could do this with a Python library, but I only trust ExifTool to do it correctly.
    args = ['exiftool', '-gps*=', str(file)]
    logger.debug(f'> {args}')
    subprocess.run(args, check=True)
