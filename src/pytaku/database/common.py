import apsw

DBNAME = "db.sqlite3"

_conn = None


def _row_trace(cursor, row):
    """
    Customize each result row's representation:
    - If query only asks for 1 field, return that result directly instead of tuple
    - If more than 1 field, return dict instead of tuple
    """
    desc = cursor.getdescription()
    if len(desc) == 1:
        return row[0]
    else:
        return {k[0]: row[i] for i, k in enumerate(desc)}


def get_conn():
    global _conn
    if not _conn:
        _conn = apsw.Connection(DBNAME)
        # Apparently you need to enable this pragma per connection:
        _conn.cursor().execute("PRAGMA foreign_keys = ON;")
        _conn.setrowtrace(_row_trace)
    return _conn


def run_sql(*args, **kwargs):
    return list(run_sql_on_demand(*args, **kwargs))


def run_sql_on_demand(*args, **kwargs):
    return get_conn().cursor().execute(*args, **kwargs)
