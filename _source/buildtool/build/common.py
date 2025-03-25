from dataclasses import dataclass
import logging
from pathlib import Path
import shutil

from ..photo_collection import PhotoCollection


logger = logging.getLogger(__name__)


class BuildDirectory:
    def __init__(self, root: Path, *, dry_run: bool) -> None:
        self.root = root
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
        return abs_dir_path / file_path.name


@dataclass(frozen=True)
class BuildContext:
    build_dir: BuildDirectory
    data_path: Path
    resources_path: Path
    dry_run: bool
    photos: PhotoCollection
