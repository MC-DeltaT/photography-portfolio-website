from dataclasses import dataclass, field
import logging
from pathlib import Path
import shutil

from buildtool.photo_collection import PhotoCollection
from buildtool.types import ImageID, ImageSrcSet, PhotoID, URLPath


logger = logging.getLogger(__name__)


class BuildDirectory:
    def __init__(self, root: Path, *, fast: bool, dry_run: bool) -> None:
        self.root = root
        self.fast = fast
        self.dry_run = dry_run

    def clean(self) -> None:
        logger.info(f'Deleting build directory: "{self.root}"')
        if not self.dry_run:
            if self.root.exists():
                shutil.rmtree(self.root, ignore_errors=False)

    def prepare_directory(self, dir_path: str | Path) -> Path:
        """Given a relative directory path, ensures that directory exists in the build directory.
            Returns the absolute path of the directory."""

        dir_path = Path(dir_path)
        if dir_path.is_absolute():
            raise ValueError('dir_path cannot be an absolute path')
        path = self.root / dir_path
        logger.debug(f'Creating build directory: "{path}"')
        if not self.dry_run:
            path.mkdir(parents=True, exist_ok=True)
        return path

    def prepare_file(self, file_path: str | Path) -> Path:
        """Given a relative file path, ensures the parent directory exists in the build directory.
            Returns the absolute path of the file."""

        file_path = Path(file_path)
        abs_dir_path = self.prepare_directory(file_path.parent)
        abs_file_path = abs_dir_path / file_path.name
        if not self.dry_run and abs_file_path.exists():
            raise RuntimeError('Attempting to build file that already exists, probably a mistake!')
        return abs_file_path

    def build_file(self, source_path: Path, url: URLPath) -> None:
        """Build a file that's a simple copy."""

        logger.info(f'Building URL: {url}')
        dest_path = self.prepare_file(url.fs_path)
        if self.fast:
            if not source_path.is_absolute():
                source_path = source_path.resolve()
            logger.debug(f'Symlinking file: "{source_path}" -> "{dest_path}"')
            if not self.dry_run:
                dest_path.symlink_to(source_path)
        else:
            logger.debug(f'Copying file: "{source_path}" -> "{dest_path}"')
            if not self.dry_run:
                shutil.copy(source_path, dest_path)

    def build_content(self, content: str, url: URLPath) -> None:
        """Build a file with the given content."""

        logger.info(f'Building URL: {url}')
        dest_path = self.prepare_file(url.fs_path)
        if not self.dry_run:
            dest_path.write_text(content, encoding='utf8')

    def resolve_url_path(self, url: URLPath) -> Path:
        return self.root / url.fs_path


@dataclass
class BuildState:
    photo_id_to_image_id: dict[PhotoID, ImageID] = field(default_factory=dict)
    image_srcsets: dict[ImageID, ImageSrcSet] = field(default_factory=dict)


@dataclass(frozen=True)
class BuildContext:
    build_dir: BuildDirectory
    resources_path: Path
    fast: bool
    dry_run: bool
    photos: PhotoCollection
    state: BuildState
