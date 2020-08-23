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
        # No idea what the default db busy timeout is, but apparently it's super strict:
        # got BusyError almost consistently when clicking "finish" on latest chapter,
        # making FE send both a "read" and "get title" request at roughly the same time.
        # It still makes no sense though, since "get title" is supposedly a read-only
        # operation and only "read" is a write. According to docs, WAL mode allows 1
        # writer and unlimited readers at the same time. WTF guys?
        # But anyway, until I can get to the bottom of it, let's slap on a band-aid:
        _conn.setbusytimeout(1000)
        _conn.setrowtrace(_row_trace)
    return _conn


def run_sql(*args, return_num_affected=False, **kwargs):
    cursor = run_sql_on_demand(*args, **kwargs)
    if return_num_affected:
        return cursor.execute("select changes();").fetchone()
    return list(cursor)


def run_sql_on_demand(*args, **kwargs):
    return get_conn().cursor().execute(*args, **kwargs)


def run_sql_many(*args, **kwargs):
    return get_conn().cursor().executemany(*args, **kwargs)
