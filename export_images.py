#!/usr/bin/env python3
import sys
import os
import argparse
from typing import List
import pathlib
import shutil

import photos2gphoto
from photos2gphoto import cli
from photos_app import items, structure, utils


def parse_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Browse Photos.app DB')
    cli.add_standart_db_options(parser)
    cli.add_export_options(parser)
    parser.add_argument('-o', '--output', help='Output directory', required=True)

    return parser.parse_args(args)


def main(args: List[str]) -> int:
    params = parse_args(args[1:])
    photos2gphoto.setup_logging(params)

    output_dir = pathlib.Path(params.output)
    if not output_dir.exists():
        sys.stderr.write('Output directory {} not exist'.format(output_dir))
        return 1

    db, tmp_dir = photos2gphoto.open_db(params)
    masters_path = cli.get_masters_path(params)

    album_ids = params.album_id
    print('Export albums with ids: {}'.format(', '.join(album_ids)))

    for album_id in album_ids:
        album = structure.get_album(db, album_id)
        album_items = items.get_album_items(db, album_id)
        total_size = sum((i.file_size for i in album_items))
        dir_name = utils.clean_filename(album.name) if album.name else 'unnamed'
        dir_name += ' (id={})'.format(album_id)
        album_path = output_dir.joinpath(dir_name)

        print('Found {n} {l} for the album "{a}" with id {i}. Total size: {s:.0f} MiB'.format(
            n=len(album_items),
            l='items' if abs(len(album_items)) > 1 else 'item',
            i=album_id,
            s=total_size / (1024 * 1024),
            a=album.name
        ))
        os.makedirs(album_path, mode=0o755, exist_ok=True)
        print('Copy items to {}'.format(album_path))
        any_copied = False
        for item in album_items:
            file_path = masters_path.joinpath(item.rel_path)
            if not file_path.exists():
                photos2gphoto.logger.error('Unable to found item at %s for %s, skipped', file_path, item)
            else:
                res_file_path = album_path.joinpath(utils.clean_filename(item.file_name))
                if res_file_path.exists():
                    photos2gphoto.logger.error('File at %s exist, skipped', res_file_path)
                else:
                    photos2gphoto.logger.debug('result path %s', res_file_path)
                    shutil.copyfile(file_path, res_file_path)
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    any_copied = True
        if any_copied:
            print(' Done')
        else:
            if album_items:
                print('All album items have been skipped')
            else:
                print('Album is empty')

    cli.cleanup(params, tmp_dir)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
