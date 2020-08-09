import datetime
import subprocess
from importlib import resources
from pathlib import Path

from . import migrations
from .common import DBNAME, get_conn, run_sql


"""
Forward-only DB migration scheme held together by duct tape.

- Uses `user_version` pragma to figure out what migrations are pending.
- Migrations files are in the form `./migrations/mXXXX.sql`.
"""


def _get_current_version():
    return run_sql("PRAGMA user_version;")[0]


def _get_version(migration: Path):
    return int(migration.name[len("m") : -len(".sql")])


def _get_pending_migrations(migrations_dir: Path):
    current_version = _get_current_version()
    migrations = sorted(migrations_dir.glob("m*.sql"))
    return [
        migration
        for migration in migrations
        if _get_version(migration) > current_version
    ]


def _read_migrations(paths):
    """Returns list of (version, sql_text) tuples"""
    results = []
    for path in paths:
        with open(path, "r") as sql_file:
            results.append((_get_version(path), sql_file.read()))
    return results


def _write_db_schema_script(migrations_dir: Path):
    schema = subprocess.run(
        ["sqlite3", DBNAME, ".schema"], capture_output=True, check=True
    ).stdout
    with open(migrations_dir / Path("latest_schema.sql"), "wb") as f:
        f.write(b"-- This file is auto-generated by the migration script\n")
        f.write(b"-- for reference purposes only. DO NOT EDIT.\n\n")
        f.write(schema)


def migrate(overwrite_latest_schema=True):
    # If there's no existing db, create one with the correct pragmas
    if not Path(DBNAME).is_file():
        run_sql("PRAGMA journal_mode = WAL;")

    with resources.path(migrations, "") as migrations_dir:
        pending_migrations = _get_pending_migrations(migrations_dir)
        if not pending_migrations:
            print("Nothing to migrate.")
            exit()
        print(f"There are {len(pending_migrations)} pending migrations.")
        migration_contents = _read_migrations(pending_migrations)

        conn = get_conn()
        cursor = conn.cursor()

        # Backup first
        now = datetime.datetime.utcnow().isoformat("T", "milliseconds")
        backup_filename = f"db_backup_{now}.sqlite3"
        print(f"Backup up to {backup_filename}...", end="")
        cursor.execute("VACUUM main INTO ?;", (backup_filename,))
        print(" done")

        # Start migrations
        # NOTE: this is NOT done in a transaction.
        # You'll need to do transactions inside your sql scripts.
        # This is to allow for drastic changes that require temporarily turning off the
        # foreign_keys pragma, which doesn't work inside transactions.
        # If anything goes wrong here, let it abort the whole script. You can always
        # restore from the backup file.
        cursor = conn.cursor()
        for version, sql in migration_contents:
            print("Migrating version", version, "...")
            cursor.execute(sql)
            cursor.execute(f"PRAGMA user_version = {version};")

        if overwrite_latest_schema:
            _write_db_schema_script(migrations_dir)

        print("All done. Current version:", _get_current_version())
