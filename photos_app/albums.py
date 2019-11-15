# coding: utf-8
import enum
from collections import namedtuple
from typing import List

from photos_app import db_utils, utils, tree_utils, logger


class AlbumSubclass(enum.IntEnum, utils.RichEnumTrait):
    SYS = 1  # or TOP?
    SMART = 2
    SIMPLE = 3


class Album(namedtuple('Album', ['id', 'uuid', 'folder_uuid', 'name', 'subclass', 'is_magic'])):
    pass


def get_all_albums(db):
    cursor = db_utils.execute(
        db,
        'select'
        ' modelId as id, uuid, name, albumSubclass as subclass, folderUuid as folder_uuid,'
        ' isMagic as is_magic '
        'from RKAlbum '
        'where not isInTrash and not isHidden'
    )

    return db_utils.fetch_namedtuples(
        Album, cursor, boolean_columns=['is_magic'],
        custom_columns={'subclass': utils.build_to_enum_converter(AlbumSubclass)}
    )


def append_albums_to_folders_tree(folders_tree: tree_utils.Tree, albums: List[Album]) -> tree_utils.Tree:
    merged_tree = folders_tree.clone()

    folders_index = tree_utils.build_index(merged_tree, lambda n: n.uuid)
    for album in albums:
        if album.folder_uuid in folders_index:
            folder = folders_index[album.folder_uuid]
            folder.insert_child_value(album)
        else:
            logger.warn("album with out folder: %r", album)
    return merged_tree
