#!/usr/bin/env python3
import argparse
import sys
from argparse import Namespace
from pathlib import Path
import shutil
import logging

import photos_app
from photos_app import folders, albums


def parse_args(args) -> Namespace:
    default_db_path = Path.home().joinpath('Pictures', 'Photos Library.photoslibrary', 'database', 'photos.db')
    parser = argparse.ArgumentParser(description='Browse Photos.app DB')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('-d', '--db', help='DB path', default=str(default_db_path))
    parser.add_argument('--no-snapshot', help="Don't make database file snapshot to temporary location",
                        action='store_true', default=False)

    return parser.parse_args(args)


def main(args) -> int:
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

    if params.no_snapshot:
        db = photos_app.open_inplace(params.db)
        tmp_dir = None
    else:
        tmp_dir, db = photos_app.open_snapshot(params.db)

    folders_tree = folders.get_folders_tree(db)

    def node_format(node):
        if isinstance(node, folders.Folder):
            return '📂 {name}    (magic={magic}, uuid={uuid})'.format(
                name=node.name if node.name is not None else '<unnamed>',
                magic='Y' if node.is_magic else 'N',
                uuid=node.uuid
            )
        elif isinstance(node, albums.Album):
            return '🖼 {name}    (magic={magic}, uuid={uuid})'.format(
                name=node.name if node.name is not None else '<unnamed>',
                magic='Y' if node.is_magic else 'N',
                uuid=node.uuid
            )
        else:
            return str(node)

    albums_list = albums.get_all_albums(db)
    folders_and_albums_tree = albums.append_albums_to_folders_tree(folders_tree, albums_list)

    print('Folders & albums')
    folders_and_albums_tree.print(node_format)

    if tmp_dir is not None:
        if not params.debug:
            logging.debug('Clean up tmp dir %s', tmp_dir)
            shutil.rmtree(tmp_dir)
        else:
            logging.debug('Leaving tmp dir %s', tmp_dir)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
