import apsw

DBNAME = "db.sqlite3"


def get_conn():
    return apsw.Connection(DBNAME)
