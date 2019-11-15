# coding: utf-8
import sqlite3
from collections import namedtuple

from photos_app import db_utils
from photos_app.tree_utils import Tree, TreeNode
from photos_app import PhotosAppError, logger


class Folder(namedtuple('Folder', ['id', 'uuid', 'name', 'parent_uuid', 'is_magic'])):
    pass


def get_folders_tree(db: sqlite3.Connection) -> Tree:
    all_folders_query = (
        "select modelId as id, uuid, name, parentFolderUuid as parent_uuid, isMagic as is_magic "
        "from RKFolder "
        "where not isHidden and inTrashDate is null"
    )

    root_nodes = []

    raw_folders = db_utils.fetch_namedtuples(
        Folder, db_utils.execute(db, all_folders_query), boolean_columns=['is_magic']
    )

    level = 0
    append = True
    nodes_index = dict()
    while append:
        append = False
        for folder in raw_folders.copy():
            folder_node = TreeNode(folder)
            if level == 0 and folder.parent_uuid is None:
                root_nodes.append(folder_node)
                append = True
            elif folder.parent_uuid is not None and folder.parent_uuid in nodes_index:
                nodes_index[folder.parent_uuid].insert_child(folder_node)
                append = True

            if append:
                nodes_index[folder.uuid] = folder_node
                raw_folders.remove(folder)

        level += 1
        if level > 100:
            logger.debug('Intermediate tree:\n%s', Tree(root_nodes=root_nodes).format())
            raise PhotosAppError("Too deep tree for folders")

    return Tree(root_nodes=root_nodes)
