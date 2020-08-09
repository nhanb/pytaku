import json
import re

import apsw
import requests

from mangoapi.base_site import Site

regexes = {
    "title_name": re.compile(r"<title>\s*([^|]+) | MangaSee</title>"),
    "title_chapters": re.compile(r"vm\.Chapters = (\[[^\]]+\])"),
}


class Mangasee(Site):
    search_table = None

    def __init__(self, keyval_store=None):
        self.keyval_store = keyval_store

    def get_title(self, title_id):
        resp = requests.get(f"https://mangasee123.com/manga/{title_id}", timeout=3)
        assert resp.status_code == 200
        html = resp.text
        name = regexes["title_name"].search(html).group(1).strip()
        chapters_str = regexes["title_chapters"].search(html).group(1)
        chapters = [
            {
                "id": ch["Chapter"],
                "name": ch["ChapterName"],
                "volume": "",
                "groups": [],
                **_parse_chapter_number(ch["Chapter"]),
            }
            for ch in json.loads(chapters_str)
        ]
        return {
            "id": title_id,
            "name": name,
            "site": "mangasee",
            "cover_ext": "jpg",
            "chapters": chapters,
            "alt_names": [],
            "descriptions": [],
        }

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

    def title_cover(self, title_id, cover_ext):
        return f"https://cover.mangabeast01.com/cover/{title_id}.jpg"

    def title_source_url(self, title_id):
        return f"https://mangasee123.com/manga/{title_id}"


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


def _parse_chapter_number(e):
    """
    Mangasee author tries to be clever with obtuse chapter numbers that must be decoded
    via javascript:

        (vm.ChapterDisplay = function (e) {
        var t = parseInt(e.slice(1, -1)),
            n = e[e.length - 1];
        return 0 == n ? t : t + "." + n;
        })

        Example: vm.ChapterDisplay('100625') === '62.5'

    No idea why tbh.
    """
    major = int(e[1:-1])
    minor = int(e[-1])
    return {
        "num_major": major,
        "num_minor": minor,
        "number": str(major) if not minor else f"{major}.{minor}",
    }
