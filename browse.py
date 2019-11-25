#!/usr/bin/env python3
import sys
import argparse
from typing import List

import photos2gphoto
from photos2gphoto import cli


def parse_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Browse Photos.app DB')
    cli.add_standart_db_options(parser)
    cli.add_albums_and_folder_options(parser)
    return parser.parse_args(args)


def main(args: List[str]) -> int:
    params = parse_args(args[1:])
    photos2gphoto.setup_logging(params)

    db, tmp_dir = photos2gphoto.open_db(params)
    folders_and_albums = photos2gphoto.load_folders_and_albums(db, params)

    print('Folders & albums')
    folders_and_albums.print(photos2gphoto.node_format)

    cli.cleanup(params, tmp_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
