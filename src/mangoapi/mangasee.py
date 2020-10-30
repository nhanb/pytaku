import json
import re

import apsw

from mangoapi.base_site import Site

regexes = {
    "title_name": re.compile(r"<title>\s*([^|]+) | MangaSee</title>"),
    "title_chapters": re.compile(r"vm\.Chapters = (\[[^\]]+\])"),
    "title_desc": re.compile(
        r"<span +class=\"mlabel\">Description:</span>[^<]+<div[^>]*>([^<]+)<"
    ),
    "chapter_title_name": re.compile(r'vm\.IndexName = "([^"]+)"'),
    "chapter_data": re.compile(r"vm\.CurChapter = (\{[^\}]+\})"),
    "chapter_img_server": re.compile(r'vm\.CurPathName = "([^"]+)"'),
}


class Mangasee(Site):
    search_table = None

    def __init__(self, keyval_store=None):
        super().__init__()
        self.keyval_store = keyval_store

    def get_title(self, title_id):
        resp = self.http_get(f"https://mangasee123.com/manga/{title_id}")
        html = resp.text
        name = regexes["title_name"].search(html).group(1).strip()
        desc = regexes["title_desc"].search(html).group(1).strip()
        chapters_str = regexes["title_chapters"].search(html).group(1)
        chapters = []
        for ch in json.loads(chapters_str):
            numbers = _parse_chapter_number(ch["Chapter"])
            chapters.append(
                {
                    "id": numbers["number"],
                    "name": ch["ChapterName"],
                    "volume": "",
                    "groups": [],
                    **numbers,
                }
            )
        return {
            "id": title_id,
            "name": name,
            "site": "mangasee",
            "cover_ext": "jpg",
            "chapters": chapters,
            "alt_names": [],
            "descriptions": [desc],
        }

    def get_chapter(self, title_id, chapter_id):
        resp = self.http_get(
            f"https://mangasee123.com/read-online/{title_id}-chapter-{chapter_id}.html"
        )
        html = resp.text

        title_id = regexes["chapter_title_name"].search(html).group(1)
        chapter_data = json.loads(regexes["chapter_data"].search(html).group(1))
        num_pages = int(chapter_data["Page"])
        img_server = regexes["chapter_img_server"].search(html).group(1)

        numbers = _parse_chapter_number(chapter_data["Chapter"])

        result = {
            "id": chapter_id,
            "title_id": title_id,
            "site": "mangasee",
            "name": chapter_data["ChapterName"] or "",
            "pages": [
                _generate_img_src(img_server, title_id, chapter_data["Chapter"], p)
                for p in range(1, num_pages + 1)
            ],
            "pages_alt": [],
            "groups": [],
            "is_webtoon": False,
            **numbers,
        }
        return result

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
                    self.keyval_store.get("mangasee_titles", "null", since="-20 day")
                )
            if not titles:
                print("Fetching mangasee title list...", end="")
                resp = self.http_get("https://mangasee123.com/_search.php")
                print(" done")
                titles = resp.json()
                self.keyval_store.set("mangasee_titles", resp.text)
            self.search_table = SearchTable(titles)

        return [
            {
                "id": row[0],
                "name": row[1],
                "site": "mangasee",
                "thumbnail": f"https://cover.nep.li/cover/{row[0]}.jpg",
            }
            for row in self.search_table.search(query)
        ]

    def title_cover(self, title_id, cover_ext):
        return self.title_thumbnail(title_id)

    def title_thumbnail(self, title_id):
        return f"https://cover.nep.li/cover/{title_id}.jpg"

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
            "INSERT INTO titles(id, name, alt_names) VALUES(?,?,?);", rows
        )

    def search(self, query):
        query = '"' + query.replace('"', '""') + '"'
        return self.db.cursor().execute(
            "SELECT id, name FROM titles WHERE titles MATCH ? ORDER BY rank;", (query,)
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
    result = {
        "num_major": major,
        "number": str(major) if not minor else f"{major}.{minor}",
    }
    if minor:
        result["num_minor"] = minor
    return result


def _generate_img_src(img_srv, title_id, chapter_id, page):
    """
    Chapter ID padding logic:

        vm.ChapterImage = function (ChapterString) {
          var Chapter = ChapterString.slice(1, -1);
          var Odd = ChapterString[ChapterString.length - 1];
          if (Odd == 0) {
            return Chapter;
          } else {
            return Chapter + "." + Odd;
          }
        };
    """
    chapter = chapter_id[1:-1]
    odd = chapter_id[len(chapter_id) - 1]
    if odd == "0":
        padded_chapter = chapter
    else:
        padded_chapter = f"{chapter}.{odd}"
    return f"https://{img_srv}/manga/{title_id}/{padded_chapter}-{page:03d}.png"
