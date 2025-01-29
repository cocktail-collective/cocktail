__all__ = [
    "get_connection",
    "insert_page",
    "get_db_update_period",
    "get_last_updated",
    "set_last_updated",
    "calculate_period",
]

import json
import os
import time
import logging
import typing
import datetime
import platformdirs
import importlib.resources
from PySide6 import QtSql
from cocktail.core.database import data_classes

CURRENT_SCHEMA_VERSION = 3

logger = logging.getLogger(__name__)


def insert_or_replace(db, table_name, rows: typing.Iterable[typing.NamedTuple]):
    if not rows:
        logger.warning(f"Nothing to insert into {table_name}, rows is empty.")
        return

    start = time.time()
    column_names = [name for name in rows[0]._fields]

    column_names = ", ".join(column_names)
    placeholder = ", ".join(["?"] * len(rows[0]._fields))

    statement = (
        f"INSERT OR REPLACE INTO {table_name} ({column_names}) VALUES({placeholder})"
    )

    db.transaction()
    for row in rows:
        if not row:
            logger.warning(f"Empty row found in {table_name}, discarding.")
            continue

        query = QtSql.QSqlQuery(db)
        query.prepare(statement)

        for index, value in enumerate(row):
            if isinstance(value, (list, dict)):
                value = json.dumps(value)

            query.bindValue(index, value)

        if not query.exec():
            logger.error(f"Failed to execute statement: {statement} for row {row}")
            raise RuntimeError(
                f"Failed to execute statement: {query.lastQuery()}, {query.lastError().text()}"
            )

    db.commit()

    logger.debug(
        f"Inserted {len(rows)} rows into {table_name} in {time.time() - start:.2f}s"
    )


def insert_page(db, page: data_classes.Page):
    insert_or_replace(db, "model", page.models)
    insert_or_replace(db, "model_version", page.versions)
    insert_or_replace(db, "model_file", page.files)
    insert_or_replace(db, "model_image", page.images)


def get_last_updated(db):
    query = QtSql.QSqlQuery(db)
    query.prepare("SELECT value FROM metadata WHERE key = 'last_updated'")

    if not query.exec():
        raise RuntimeError(f"Failed to execute statement: {query.lastError().text()}")

    if not query.next():
        return None

    return datetime.datetime.fromisoformat(query.value(0))


def set_last_updated(db, dt: datetime.datetime = None):
    dt = dt or datetime.datetime.now()
    query = QtSql.QSqlQuery(db)
    query.prepare(
        "INSERT OR REPLACE INTO metadata (key, value) VALUES('last_updated', ?)"
    )
    query.bindValue(0, dt.isoformat())

    if not query.exec():
        raise RuntimeError(f"Failed to execute statement: {query.lastError().text()}")


def create_tables(db):
    """
    populates the database with the schema defined in schema.sql
    """
    logger.info("creating new database")

    schema = importlib.resources.read_text("cocktail.core.database", "schema.sql")
    statements = [statement.strip() for statement in schema.split(";")]
    for statement in statements:
        if not statement:
            continue

        query = QtSql.QSqlQuery(statement, db)
        if not query.exec():
            logger.error(f"Failed to execute statement: {statement}")
            logger.error(query.lastError().text())
            return False

    query = QtSql.QSqlQuery(db)
    query.prepare("PRAGMA user_version = ?")
    query.bindValue(0, CURRENT_SCHEMA_VERSION)
    query.exec()

    epoch = datetime.datetime.fromtimestamp(0)
    set_last_updated(db, epoch)


def get_db_update_period(db):
    last_updated = get_last_updated(db)
    return calculate_period(last_updated)


def calculate_period(last_updated):
    now = datetime.datetime.now()
    days = (now - last_updated).days

    if days <= 2:
        return data_classes.Period.Day
    elif days <= 7:
        return data_classes.Period.Week
    elif days <= 30:
        return data_classes.Period.Month
    elif days <= 365:
        return data_classes.Period.Year
    else:
        return data_classes.Period.AllTime


def get_database_path():
    dirname = platformdirs.user_cache_dir("cocktail", "cocktail")
    return os.path.join(dirname, "cocktail.sqlite3")


def get_connection(filepath=None):
    filepath = filepath or get_database_path()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    logger.info(f"Connecting to database at {filepath}")

    db = QtSql.QSqlDatabase.addDatabase("QSQLITE", "cocktail")
    db.setDatabaseName(filepath)
    db.open()

    if not db.tables():
        create_tables(db)

    return db


def get_schema_version(db):
    """
    Returns the schema version of the database.
    """
    query = QtSql.QSqlQuery(db)
    query.prepare("PRAGMA user_version")

    if not query.exec():
        raise RuntimeError(f"Failed to execute statement: {query.lastError().text()}")

    if not query.next():
        raise RuntimeError("Failed to get schema version")
    version = query.value(0)
    logger.info("user version: {}".format(version))
    return version
