# encoding: utf-8
import sqlite3
import os
import os.path
import tempfile
import shutil
from typing import Tuple
import logging

logger = logging.getLogger("photos_app")


class PhotosAppError(Exception):
    pass


def _log_file_size(file_path, label):
    stat = os.stat(file_path)
    if hasattr(stat, 'st_rsize'):
        size = stat.st_rsize
    else:
        size = stat.st_size
    logger.debug('%s size %0.1f MB', label, size / 1024 / 1024)


def open_snapshot(db_path) -> Tuple[str, sqlite3.Connection]:
    if not os.path.isfile(db_path):
        raise PhotosAppError("Unable to find db at '{}'".format(db_path))

    if logger.isEnabledFor(logging.DEBUG):
        _log_file_size(db_path, 'DB')

    tmp_dir = tempfile.mkdtemp(prefix='photos_db_snapshot')
    logger.debug('Create temp dir at %s', tmp_dir)
    snapshot_path = os.path.join(tmp_dir, 'snapshot.db')
    shutil.copy(db_path, snapshot_path)

    wal_path = db_path + "-wal"
    wal_snapshot_path = snapshot_path + "-wal"
    if os.path.isfile(wal_path):
        logger.debug('WAL found at %s', wal_path)
        if logger.isEnabledFor(logging.DEBUG):
            _log_file_size(wal_path, 'DB WAL')
        shutil.copy(wal_path, wal_snapshot_path)

    return tmp_dir, open_inplace(snapshot_path)


def open_inplace(path) -> sqlite3.Connection:
    if not os.path.isfile(path):
        raise PhotosAppError("Unable to find db at '{}'".format(path))

    connection = sqlite3.connect('file:{}?mode=ro'.format(path), uri=True)
    connection.row_factory = sqlite3.Row
    return connection
