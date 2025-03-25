from pathlib import Path
import logging
import tempfile
import shutil

from .image import strip_image_exif_gps
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
        logger.info(f'Ingesting photo: {photo}')

        assert photo.image_file_path.parent == photo.metadata_file_path.parent
        dest_dir = photo_resources_path / photo.image_file_path.parent.relative_to(ingest_path)

        # Copy file to temporary directory while modifying it to provide strong exception guarantee.
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_image_file = Path(tmp_dir) / photo.image_file_path.name
            shutil.copyfile(photo.image_file_path, tmp_image_file)

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
        # Remove everything in the ingest directory, which should be empty if the ingest operation succeeded.
        for entry in ingest_path.iterdir():
            if entry.is_dir():
                shutil.rmtree(entry, ignore_errors=False)
            else:
                entry.unlink()
