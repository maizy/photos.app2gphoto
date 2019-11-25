# coding: utf-8
from pathlib import Path
import argparse
import shutil

import photos2gphoto


def add_standart_db_options(parser: argparse.ArgumentParser):
    default_db_path = Path.home().joinpath('Pictures', 'Photos Library.photoslibrary', 'database', 'photos.db')
    parser.add_argument('-d', '--db', default=str(default_db_path), help='DB path')
    parser.add_argument('--no-snapshot', action='store_true', default=False,
                        help="Don't make database file snapshot to temporary location")

    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)


def add_albums_and_folder_options(parser: argparse.ArgumentParser):
    parser.add_argument('--no-skip-projects', action='store_true', default=False,
                        help='Skip folder & albums in Projects folder (folder exist if you migrate your library'
                             ' from old iPhoto app. it\'s always empty)')


def add_export_options(parser: argparse.ArgumentParser):
    parser.add_argument('-a', '--album-id', action='append', help='Album ids', metavar='ID', required=True)
    parser.add_argument('-m', '--masters-path', help='Path to masters. By default calculated relative to DB path.',
                        default=None)


def cleanup(params: argparse.Namespace, tmp_dir: str):
    if tmp_dir is not None:
        if not params.debug:
            photos2gphoto.logger.debug('Clean up tmp dir %s', tmp_dir)
            shutil.rmtree(tmp_dir)
        else:
            photos2gphoto.logger.debug('Leaving tmp dir %s', tmp_dir)


def get_masters_path(params: argparse.Namespace) -> Path:
    if params.masters_path is not None:
        path = Path(params.masters_path)
    else:
        path = Path(Path(params.db).parent.parent, 'Masters')
    if not path.exists():
        raise photos2gphoto.PhotosAppError('Masters at {} not found'.format(path))
    photos2gphoto.logger.debug('Loading masters from %s', path)
    return path
