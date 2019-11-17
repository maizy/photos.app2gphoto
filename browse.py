#!/usr/bin/env python3
import sys
import argparse
import logging
from typing import List

import photos2gphoto
from photos2gphoto import cli


def parse_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Browse Photos.app DB')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--debug', action='store_true')
    cli.add_standart_db_options(parser)

    return parser.parse_args(args)


def main(args: List[str]) -> int:
    params = parse_args(args[1:])
    debug_logging = params.verbose or params.debug
    if debug_logging:
        logging_format = '%(asctime)s %(levelname).1s [%(name)s] %(message)s'
    else:
        logging_format = '%(asctime)s %(levelname).1s %(message)s'
    logging.basicConfig(
        level=logging.DEBUG if debug_logging else logging.INFO,
        stream=sys.stderr,
        format=logging_format,
        datefmt='%H:%M:%S'
    )

    tmp_dir, folders_and_albums = photos2gphoto.load_folders_and_albums(params)

    print('Folders & albums')
    folders_and_albums.print(photos2gphoto.node_format)

    cli.cleanup(params, tmp_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
