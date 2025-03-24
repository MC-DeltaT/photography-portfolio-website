from pathlib import Path
import logging


logger = logging.getLogger(__name__)


def run_ingest(ingest_path: Path, data_path: Path, *, dry_run: bool) -> None:
    logger.info(f'Running data ingest')
    logger.info(f'Ingest directory: "{ingest_path}"')
    logger.info(f'Data directory: "{data_path}"')

    ... # TODO
