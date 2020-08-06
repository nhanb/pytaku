import apsw

DBNAME = "db.sqlite3"

_conn = None


def get_conn():
    global _conn

    if not _conn:
        _conn = apsw.Connection(DBNAME)

        # Apparently you need to enable this pragma _per connection_
        _conn.cursor().execute("PRAGMA foreign_keys = ON;")

        # Return rows as dicts instead of tuples
        _conn.setrowtrace(
            lambda cursor, row: {
                k[0]: row[i] for i, k in enumerate(cursor.getdescription())
            }
        )

    return _conn


def run_sql(*args, **kwargs):
    cursor = get_conn().cursor()
    results = cursor.execute(*args, **kwargs)
    return list(results)
