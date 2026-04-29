import argparse
import logging
from pathlib import Path

from buildtool.build.main import run_build
from buildtool.ingest import run_ingest


logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    arg_parser.add_argument('-i', '--ingest-path', type=Path, default=Path('./ingest'), help='Directory to ingest new photos from')
    arg_parser.add_argument('-d', '--resource-path', type=Path, default=Path('./resource'), help='Directory containing source data')
    arg_parser.add_argument('-o', '--output-path', type=Path, default=Path('./site'), help='Directory to build site into')
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='Log more')
    build_mode_group = arg_parser.add_mutually_exclusive_group()
    build_mode_group.add_argument('--dry-run', action='store_true', help='Simulate actions without writing anything')
    build_mode_group.add_argument('--fast', action='store_true', help='Make the build faster by taking shortcuts (for testing only)')
    actions_group = arg_parser.add_mutually_exclusive_group()
    actions_group.add_argument('--ingest', action=argparse.BooleanOptionalAction, default=None, help='Ingest photos')
    actions_group.add_argument('--build', action=argparse.BooleanOptionalAction, default=None, help='Build the site')

    args = arg_parser.parse_args()
    ingest_path: Path = args.ingest_path
    resource_path: Path = args.resource_path
    output_path: Path = args.output_path
    verbose: bool = args.verbose == True
    dry_run: bool = args.dry_run == True
    fast: bool = args.fast == True

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        # PIL spams debug logs we don't need
        logging.getLogger('PIL').setLevel(logging.INFO)
        logger.info('DRY RUN - won\'t write output')

    if fast:
        logging.info('Fast mode enabled')

    if args.ingest is None and args.build is None:
        ingest = True
        build = True
    else:
        ingest = args.ingest == True
        build = args.build == True

    if ingest:
        run_ingest(ingest_path, resource_path, dry_run=dry_run)

    if build:
        run_build(output_path, resource_path, fast=fast, dry_run=dry_run)


if __name__ == '__main__':
    main()
