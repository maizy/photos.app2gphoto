# coding: utf-8
import enum
from collections import namedtuple
from typing import List
import sqlite3

from photos_app import db_utils, utils, tree_utils, logger, PhotosAppError

TOP_LEVEL_ALBUMS_UUID = 'TopLevelAlbums'
LIBRARY_FOLDER_UUID = 'LibraryFolder'
PROJECTS_FOLDERS_UUID = 'AllProjectsItem'


class AlbumSubclass(enum.IntEnum, utils.RichEnumTrait):
    SYS = 1  # or TOP?
    SMART = 2
    SIMPLE = 3


class Album(namedtuple('Album', ['id', 'uuid', 'folder_uuid', 'name', 'subclass', 'is_magic', 'items_count'])):
    pass


class Folder(namedtuple('Folder', ['id', 'uuid', 'name', 'parent_uuid', 'is_magic'])):
    pass


def get_all_albums(db):
    cursor = db_utils.execute(
        db,
        'select'
        ' RKAlbum.modelId as id, RKAlbum.uuid, RKAlbum.name, RKAlbum.albumSubclass as subclass, '
        ' RKAlbum.folderUuid as folder_uuid, RKAlbum.isMagic as is_magic, count(RKVersion.modelId) as items_count '
        'from RKAlbum '
        'left join RKAlbumVersion on RKAlbum.modelId == RKAlbumVersion.albumId '
        'left join main.RKVersion on RKAlbumVersion.versionId = RKVersion.modelId '
        'where '
        '  not RKAlbum.isInTrash and not RKAlbum.isHidden and '
        '  RKVersion.modelId is null or (not RKVersion.isInTrash and not RKVersion.isHidden) '
        '  group by RKAlbum.modelId'
    )

    return db_utils.fetch_namedtuples(
        Album, cursor, boolean_columns=['is_magic'],
        custom_columns={'subclass': utils.build_to_enum_converter(AlbumSubclass)}
    )


def find_by_uuid(uuid):
    def _matcher(node):
        if node.value.uuid == uuid:
            return node
        return None
    return _matcher


def append_albums_to_folders_tree(folders_tree: tree_utils.Tree, albums: List[Album]) -> tree_utils.Tree:
    merged_tree = folders_tree.clone()
    if not merged_tree.root_nodes:
        logger.error('Empty folders tree, unable to append albums to folders')
        return merged_tree

    default_root = merged_tree.find_first(find_by_uuid(TOP_LEVEL_ALBUMS_UUID)) or \
        merged_tree.find_first(find_by_uuid(LIBRARY_FOLDER_UUID)) or \
        merged_tree.root_nodes[0]

    folders_index = tree_utils.build_index(merged_tree, lambda n: n.uuid)
    for album in albums:
        if album.folder_uuid in folders_index:
            folder = folders_index[album.folder_uuid]
            folder.insert_child_value(album)
        else:
            logger.debug("album without folder: %r, append to %r", album, default_root.value)
            default_root.insert_child_value(album)
    return merged_tree


def get_folders_tree(db: sqlite3.Connection) -> tree_utils.Tree:
    all_folders_query = (
        'select modelId as id, uuid, name, parentFolderUuid as parent_uuid, isMagic as is_magic '
        'from RKFolder '
        'where not isHidden and inTrashDate is null'
    )

    root_nodes = []

    raw_folders = db_utils.fetch_namedtuples(
        Folder, db_utils.execute(db, all_folders_query), boolean_columns=['is_magic']
    )

    level = 0
    append = True
    nodes_index = dict()
    while append:
        logger.debug('Folder stack size = %d before level %d', len(raw_folders), level)
        for folder in raw_folders.copy():
            append = False
            folder_node = tree_utils.TreeNode(folder)
            if level == 0 and folder.parent_uuid is None:
                root_nodes.append(folder_node)
                append = True
            elif folder.parent_uuid is not None and folder.parent_uuid in nodes_index:
                nodes_index[folder.parent_uuid].insert_child(folder_node)
                append = True

            if append:
                nodes_index[folder.uuid] = folder_node
                raw_folders.remove(folder)

        if not raw_folders:
            break
        logger.debug('Folder stack size = %d after level %d', len(raw_folders), level)
        level += 1
        if level > 100:
            logger.debug('Intermediate tree:\n%s', tree_utils.Tree(root_nodes=root_nodes).format())
            logger.debug('Folder stack size = %d', len(raw_folders))
            raise PhotosAppError("Unable to build folders tree")

    return tree_utils.Tree(root_nodes=root_nodes)
