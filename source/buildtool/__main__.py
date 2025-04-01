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
    arg_parser.add_argument('-i', '--ingest', type=Path, default=Path('../ingest'), help='Directory to ingest new photos from')
    arg_parser.add_argument('-d', '--data', type=Path, default=Path('./data'), help='Directory containing source data')
    arg_parser.add_argument('-o', '--output', type=Path, default=Path('../site'), help='Directory to build site into')
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='Log more')
    arg_parser.add_argument('--dry-run', action='store_true', help='Simulate actions without writing anything')
    arg_parser.add_argument('--fast', action='store_true', help='Make the build faster by taking shortcuts (for testing only)')

    args = arg_parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        # PIL spams debug logs we don't need
        logging.getLogger('PIL').setLevel(logging.INFO)
        logger.info('DRY RUN - won\'t write output')
    
    if args.dry_run and args.fast:
        arg_parser.error('fast should not be used with dry_run')

    run_ingest(args.ingest, args.data, dry_run=args.dry_run)

    run_build(args.output, args.data, fast=args.fast, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
