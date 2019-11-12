# coding: utf-8
import sqlite3

from photos_app import logger


def fetch_namedtuples(constructor, cursor: sqlite3.Cursor, boolean_columns=..., custom_columns=...):
    results = []
    first = True
    columns = None
    for row in cursor:
        if first:
            columns = row.keys()
        values = dict(zip(columns, row))
        if boolean_columns is not ...:
            for col in boolean_columns:
                values[col] = bool(values[col])
        if custom_columns is not ...:
            for col, func in custom_columns.items():
                values[col] = func(values[col])
        results.append(constructor(**values))
    return results


def execute(db: sqlite3.Connection, query: str, params=...) -> sqlite3.Cursor:
    logger.debug('DB query:\n%s\nparams: %s', query, params if params is not ... else '-')
    if params is ...:
        return db.execute(query)
    else:
        return db.execute(query, params)
