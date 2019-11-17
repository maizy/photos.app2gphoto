# Photos.app to Google Photo

## Usage

```
cd photos.app2gphoto/
python3 ./browse.py --help
```

Known problem: unable to access to photos.db in macOS 10.14+. Your should copy `photos.db`, 
`photos.db-wal` from `~/Pictures/Photos Library.photoslibrary/database` manually and set `--db` option.
