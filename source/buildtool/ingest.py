import logging
import os
from pathlib import Path
import tempfile

from buildtool.image import reencode_image, strip_image_exif_gps
from buildtool.resource.common import get_resources_path
from buildtool.resource.photo import PhotoMetadataFile, find_photos, get_photo_resources_path


logger = logging.getLogger(__name__)


IMAGE_MAX_DIMENSION = 3000
IMAGE_QUALITY = 85


def run_ingest(ingest_path: Path, data_path: Path, *, dry_run: bool) -> None:
    logger.info(f'Running data ingest')
    logger.info(f'Ingest directory: "{ingest_path}"')
    logger.info(f'Data directory: "{data_path}"')

    # The file structure is the same as when stored in the resources directory,
    # so we can reuse this code.
    photos = find_photos(ingest_path, skip_invalid=True)

    # Validate metadata file.
    logger.info('Validating photo metadata files')
    for photo in photos:
        _ = PhotoMetadataFile.from_file(photo.metadata_file_path)

    resources_path = get_resources_path(data_path)
    photo_resources_path = get_photo_resources_path(resources_path)

    logger.info('Ingesting photos into resources')
    for photo in photos:
        logger.info(f'Ingesting photo: {photo}')

        # Store the photo in the resources directory in the same structure as it is in the ingest directory.
        # It doesn't really matter what the structure is in the resources directory, other than filenames not conflicting.
        # This way, we offload the issue of filename uniqueness to the user and simplify the code.
        assert photo.image_file_path.parent == photo.metadata_file_path.parent
        dest_dir = photo_resources_path / photo.image_file_path.parent.relative_to(ingest_path)

        # Copy file to temporary directory while modifying it to provide strong exception guarantee.
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_image_file = Path(tmp_dir) / photo.image_file_path.name
            
            # Reduce the image size and quality because the originals will take up way too much space eventually.
            logger.debug('Reencoding image')
            reencode_image(photo.image_file_path, tmp_image_file, IMAGE_MAX_DIMENSION, IMAGE_QUALITY)
            if not tmp_image_file.exists():
                raise RuntimeError(f'Failed to reencode image: "{photo.image_file_path}"')

            # Some modifications to the image to make it appropriate for web publishing.
            logger.debug('Stripping image of EXIF GPS tags')
            strip_image_exif_gps(tmp_image_file)

            # Move the tmp image to the resources directory.
            logger.debug(f'Creating directory: "{dest_dir}"')
            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
            dest_image_file = dest_dir / photo.image_file_path.name
            logger.debug(f'Moving image file: "{tmp_image_file}" -> "{dest_image_file}"')
            if not dry_run:
                tmp_image_file.rename(dest_image_file)
        # Move the metadata file to the resources directory alongside the image file.
        dest_metadata_file = dest_dir / photo.metadata_file_path.name
        logger.debug(f'Moving metadata file: "{photo.metadata_file_path}" -> "{dest_metadata_file}"')
        if not dry_run:
            photo.metadata_file_path.rename(dest_metadata_file)

        if not dry_run:
            # Remove the original image
            photo.image_file_path.unlink()

    if not dry_run:
        # Remove empty subdirectories in the ingest folder.
        for root, dirs, files in os.walk(ingest_path, topdown=False):
            if not files and not dirs and root != str(ingest_path):
                logger.debug(f'Removing empty directory: "{root}"')
                os.rmdir(root)
