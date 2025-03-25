from pathlib import Path
import logging
import tempfile
from shutil import copyfile
import subprocess

from .resource.common import get_resources_path
from .resource.photo import PhotoMetadataFile, find_photos, get_photo_resources_path


logger = logging.getLogger(__name__)


def run_ingest(ingest_path: Path, data_path: Path, *, dry_run: bool) -> None:
    logger.info(f'Running data ingest')
    logger.info(f'Ingest directory: "{ingest_path}"')
    logger.info(f'Data directory: "{data_path}"')

    # The file structure is the same as when stored in the resources directory,
    # so we can reuse this code.
    photos = find_photos(ingest_path)

    # Validate metadata file.
    logger.info('Validating photo metadata files')
    for photo in photos:
        _ = PhotoMetadataFile.from_file(photo.metadata_file_path)

    resources_path = get_resources_path(data_path)
    photo_resources_path = get_photo_resources_path(resources_path)

    logger.info('Ingesting photos into resources')
    for photo in photos:
        logger.debug(f'Ingesting photo: {photo}')

        assert photo.image_file_path.parent == photo.metadata_file_path.parent
        dest_dir = photo_resources_path / photo.image_file_path.parent.relative_to(ingest_path)

        # Copy file to temporary directory while modifying it to provide strong exception guarantee.
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_image_file = Path(tmp_dir) / photo.image_file_path.name
            copyfile(photo.image_file_path, tmp_image_file)
            logger.debug('Stripping image of EXIF GPS tags')
            strip_image_exif_gps(tmp_image_file)
            logger.debug('Reducing image file size')
            reduce_image_file_size(tmp_image_file)
            logger.debug(f'Creating directory: "{dest_dir}"')
            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
            dest_image_file = dest_dir / photo.image_file_path.name
            logger.debug(f'Moving image file: "{tmp_image_file}" -> "{dest_image_file}"')
            if not dry_run:
                tmp_image_file.rename(dest_image_file)
        dest_metadata_file = dest_dir / photo.metadata_file_path.name
        logger.debug(f'Moving metadata file: "{photo.metadata_file_path}" -> "{dest_metadata_file}"')
        if not dry_run:
            photo.metadata_file_path.rename(dest_metadata_file)


def strip_image_exif_gps(file: Path) -> None:
    """Remove all GPS EXIF tags from an image in place.
        Reason is to avoid people stalking us from photo content."""

    subprocess.run(['exiftool.exe' '-gps*=', str(file)], check=True)


def reduce_image_file_size(file: Path) -> None:
    """Reduces the image dimensions and encoding quality to minimise file size."""

    MAX_DIM = 2000
    QUALITY = 80
    args = [
        'magick.exe', 'convert', str(file),
        '-resize', f'{MAX_DIM}x{MAX_DIM}'
        '-quality', str(QUALITY),
        str(file)
    ]
    subprocess.run(args, check=True)
