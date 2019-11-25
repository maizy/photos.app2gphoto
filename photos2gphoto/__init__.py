# coding: utf-8
import argparse
import logging
import sys
from typing import Tuple, Any, Optional
import sqlite3

import photos_app
from photos_app import structure, tree_utils

logger = logging.getLogger('photos2gphoto')


class PhotosAppError(Exception):
    pass


def node_format(value: Any) -> str:
    if isinstance(value, structure.Folder):
        return '📂  {name}    (id={id}{magic})'.format(
            name=value.name if value.name else '<unnamed>',
            magic=', magic=Y' if value.is_magic else '',
            id=value.id
        )
    elif isinstance(value, structure.Album):
        return '🖼  {name}    ({items} {items_label}, id={id}{magic})'.format(
            items=value.items_count,
            items_label='items' if abs(value.items_count) > 1 else 'item',
            name=value.name if value.name else '<unnamed>',
            magic=', magic=Y' if value.is_magic else '',
            id=value.id
        )
    else:
        return str(value)


def open_db(params: argparse.Namespace) -> Tuple[sqlite3.Connection, Optional[str]]:
    if params.no_snapshot:
        db = photos_app.open_inplace(params.db)
        tmp_dir = None
    else:
        tmp_dir, db = photos_app.open_snapshot(params.db)
    return db, tmp_dir


def load_folders_and_albums(db: sqlite3.Connection, params: argparse.Namespace) -> tree_utils.Tree:
    folders_tree = structure.get_folders_tree(db)

    albums_list = structure.get_all_albums(db)
    folders_and_albums_tree = structure.append_albums_to_folders_tree(folders_tree, albums_list)

    if not params.no_skip_projects:
        folders_and_albums_tree.remove_first(structure.find_in_tree_by_uuid(structure.PROJECTS_FOLDERS_UUID))

    return folders_and_albums_tree


def setup_logging(params: argparse.Namespace):
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
