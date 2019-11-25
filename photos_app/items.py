# coding: utf-8
import sqlite3
import collections
from typing import Union, List

from photos_app.structure import Album
from photos_app import db_utils


class Item(collections.namedtuple('Item', ['master_id', 'version_id', 'link_id', 'album_id', 'name',
                                           'file_name', 'rel_path', 'file_size'])):
    pass


def get_album_items(db: sqlite3.Connection, album_id: Union[str, Album]) -> List[Item]:
    album_id = album_id.id if isinstance(album_id, Album) else album_id

    query = '''\
    select
        RKMaster.modelId as master_id,
        RKVersion.modelId as version_id,
        RKAlbumVersion.modelId as link_id,
        RKAlbumVersion.albumId as album_id,
        coalesce(RKVersion.name, RKVersion.fileName) as name,
        RKVersion.fileName as file_name,
        RKMaster.imagePath as rel_path,
        RKMaster.fileSize as file_size
    from main.RKAlbumVersion
    join main.RKVersion on RKAlbumVersion.versionId = RKVersion.modelId
    join main.RKMaster on RKVersion.masterId = RKMaster.modelId
    where not RKVersion.isInTrash and not RKVersion.isHidden
    and RKAlbumVersion.albumId = ?
    '''

    return db_utils.fetch_namedtuples(Item, db_utils.execute(db, query, (album_id, )), int_columns=['file_size'])
