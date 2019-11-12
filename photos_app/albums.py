# coding: utf-8
import enum
from collections import namedtuple

from photos_app.tree_utils import Tree


class AlbumSubclass(enum.Enum):
    SYS = 1  # or TOP?
    SMART = 2
    SIMPLE = 3


class Album(namedtuple('Album', ['uuid', 'name', 'subclass'])):
    pass


# TODO
def get_albums(db):
    pass


# TODO
def append_albums_to_folders_tree(folders_tree, albums) -> Tree:
    pass
