import argparse
import logging
from pathlib import Path

from .build import run_build


logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    arg_parser.add_argument('-d', '--data', type=Path, default=Path('./data'), help='Directory containing source data')
    arg_parser.add_argument('-o', '--output', type=Path, default=Path('../site'), help='Directory to build site into')
    arg_parser.add_argument('-v', '--verbose', action='store_true', help='Log more')
    arg_parser.add_argument('--dry-run', action='store_true', help='Simulate actions without writing anything')

    args = arg_parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info('DRY RUN - won\'t write output')
    
    # TODO: run ingest

    run_build(args.output, args.data, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
