import apsw

DBNAME = "db.sqlite3"

_conn = None


def get_conn():
    global _conn
    if not _conn:
        _conn = apsw.Connection(DBNAME)
        # Apparently you need to enable this pragma _per connection_
        _conn.cursor().execute("PRAGMA foreign_keys = ON;")
    return _conn
