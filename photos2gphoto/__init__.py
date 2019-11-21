# coding: utf-8
import argparse
import logging
from typing import Tuple, Any

import photos_app
from photos_app import structure, tree_utils

logger = logging.getLogger('photos2gphoto')


def node_format(value: Any) -> str:
    if isinstance(value, structure.Folder):
        return '📂  {name}    (magic={magic}, id={id})'.format(
            name=value.name if value.name else '<unnamed>',
            magic='Y' if value.is_magic else 'N',
            id=value.id
        )
    elif isinstance(value, structure.Album):
        return '🖼  {name}    (magic={magic}, id={id})'.format(
            name=value.name if value.name else '<unnamed>',
            magic='Y' if value.is_magic else 'N',
            id=value.id
        )
    else:
        return str(value)


def load_folders_and_albums(params: argparse.Namespace) -> Tuple[str, tree_utils.Tree]:
    if params.no_snapshot:
        db = photos_app.open_inplace(params.db)
        tmp_dir = None
    else:
        tmp_dir, db = photos_app.open_snapshot(params.db)

    folders_tree = structure.get_folders_tree(db)

    albums_list = structure.get_all_albums(db)
    folders_and_albums_tree = structure.append_albums_to_folders_tree(folders_tree, albums_list)

    if params.fix_projects:
        folders_and_albums_tree = structure.fix_projects_folder(folders_and_albums_tree)

    return tmp_dir, folders_and_albums_tree
