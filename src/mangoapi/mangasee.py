import json

import apsw
import requests

from mangoapi.base_site import Site


class Mangasee(Site):
    search_table = None

    def __init__(self, keyval_store=None):
        self.keyval_store = keyval_store

    def get_title(self, title_id):
        pass

    def get_chapter(self, chapter_id):
        pass

    def search_title(self, query):
        """
        Json blob of all mangasee titles: https://mangasee123.com/_search.php
        The structure is something like this:
            [
                {
                'i': '',
                's': '',
                'a': ['', '']
                }
            ]
        Where `i` is id, `s` is name, and `a` is a list of alternative names.
        So we can just read that once and build an in-memory sqlite db for offline full
        text search.

        Additionally, if we have a local key-value store, try that before actually
        sending an http request to mangasee.
        """
        if not self.search_table:
            titles = None
            if self.keyval_store:
                titles = json.loads(
                    self.keyval_store.get("mangasee_titles", "null", since="-1 day")
                )
            if not titles:
                print("Fetching mangasee title list...", end="")
                resp = requests.get("https://mangasee123.com/_search.php")
                print(" done")
                titles = resp.json()
                self.keyval_store.set("mangasee_titles", resp.text)
            self.search_table = SearchTable(titles)

        return [
            {
                "id": row[0],
                "name": row[1],
                "site": "mangasee",
                "thumbnail": f"https://cover.mangabeast01.com/cover/{row[0]}.jpg",
            }
            for row in self.search_table.search(query)
        ]


class SearchTable:
    def __init__(self, titles: list):
        self.db = apsw.Connection(":memory:")
        cursor = self.db.cursor()
        cursor.execute(
            "CREATE VIRTUAL TABLE titles USING FTS5(id UNINDEXED, name, alt_names);"
        )

        rows = []
        for t in titles:
            id = t["i"]
            name = t["s"]
            alt_names = t["a"]
            rows.append((id, name, " ".join(alt_names)))

        cursor.executemany(
            "INSERT INTO titles(id, name, alt_names) VALUES(?,?,?);", rows,
        )

    def search(self, query):
        return self.db.cursor().execute(
            "SELECT id, name FROM titles(?) ORDER BY rank;", (query,)
        )
