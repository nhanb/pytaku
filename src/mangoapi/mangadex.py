import html
import re
import time

import bbcode

from mangoapi.base_site import Site, requires_login

MANGAPLUS_GROUP_ID = 9097
LONG_STRIP_TAG_ID = 36

_bbparser = bbcode.Parser()
_bbparser.add_simple_formatter(
    "spoiler", "<details><summary>Spoiler</summary>%(value)s</details>"
)


class Mangadex(Site):
    def get_title(self, title_id):
        url = f"https://mangadex.org/api/v2/manga/{title_id}?include=chapters"
        md_resp = self.http_get(url)
        md_json = md_resp.json()
        assert md_json["status"] == "OK"
        manga = md_json["data"]["manga"]
        chapters = md_json["data"]["chapters"]
        groups = md_json["data"]["groups"]
        groups_dict = {group["id"]: group["name"] for group in groups}

        cover = manga["mainCover"].split("/")[-1]
        cover_ext = cover[cover.find(".") + 1 : cover.rfind("?")]

        current_timestamp = time.time()

        title = {
            "id": title_id,
            "name": manga["title"],
            "site": "mangadex",
            "cover_ext": cover_ext,
            "alt_names": manga["altTitles"],
            "descriptions": [
                _bbparser.format(paragraph)
                for paragraph in html.unescape(manga["description"]).split("\r\n")
                if paragraph.strip()
            ],
            "descriptions_format": "html",
            "is_webtoon": LONG_STRIP_TAG_ID in manga["tags"],
            "chapters": [
                {
                    "id": str(chap["id"]),
                    "name": chap["title"],
                    "volume": int(chap["volume"]) if chap["volume"] else None,
                    "groups": [
                        html.unescape(groups_dict[group_id])
                        for group_id in chap["groups"]
                    ],
                    **_parse_chapter_number(chap["chapter"]),
                }
                for chap in chapters
                if chap["language"] == "gb"
                and MANGAPLUS_GROUP_ID not in chap["groups"]
                and chap["timestamp"] <= current_timestamp
                # ^ Chapter may be listed but with access delayed for a certain amount
                # of time set by uploader, in which case we just filter it out. God I
                # hate this generation of Patreon "scanlators".
            ],
        }
        return title

    def get_chapter(self, title_id, chapter_id):
        md_resp = self.http_get(
            f"https://mangadex.org/api/v2/chapter/{chapter_id}?saver=0"
        )
        md_json = md_resp.json()
        assert md_json["status"] == "OK"
        data = md_json["data"]

        # 2 cases:
        # - If 'serverFallback' is absent, it means 'server' points to MD's own server
        #   e.g. s5.mangadex.org...
        # - Otherwise, 'server' points to a likely ephemeral MD@H node, while
        # 'serverFallback' now points to MD's own server.
        #
        # MD's own links apparently go dead sometimes, but MD@H links seem to expire
        # quickly all the time, so it's probably a good idea to store both anyway.

        server_fallback = data.get("serverFallback")
        if server_fallback:
            md_server = server_fallback
            mdah_server = data["server"]
        else:
            md_server = data["server"]
            mdah_server = None

        chapter = {
            "id": chapter_id,
            "title_id": str(data["mangaId"]),
            "site": "mangadex",
            "name": data["title"],
            "pages": [f"{md_server}{data['hash']}/{page}" for page in data["pages"]],
            "pages_alt": [
                f"{mdah_server}{data['hash']}/{page}" for page in data["pages"]
            ]
            if mdah_server
            else [],
            "groups": [html.unescape(group["name"]) for group in data["groups"]],
            **_parse_chapter_number(data["chapter"]),
        }
        return chapter

    @requires_login
    def search_title(self, query):
        md_resp = self.http_get(f"https://mangadex.org/quick_search/{query}")

        matches = TITLES_PATTERN.findall(md_resp.text)
        titles = [
            {
                "id": id,
                "name": name.strip(),
                "site": "mangadex",
                "thumbnail": f"https://mangadex.org/images/manga/{id}.large.jpg",
            }
            for id, name in matches
        ]
        return titles

    def login(self, username, password):
        form_data = {
            "login_username": username,
            "login_password": password,
            "two_factor": "",
            "remember_me": "1",
        }
        self.http_post(
            "https://mangadex.org/ajax/actions.ajax.php?function=login",
            data=form_data,
            headers={"X-Requested-With": "XMLHttpRequest"},
        )
        self.is_logged_in = True

    def title_cover(self, title_id, cover_ext):
        return f"https://mangadex.org/images/manga/{title_id}.{cover_ext}"

    def title_thumbnail(self, title_id):
        return f"https://mangadex.org/images/manga/{title_id}.large.jpg"

    def title_source_url(self, title_id):
        return f"https://mangadex.org/manga/{title_id}"


# Titles regex slightly adapted from https://github.com/md-y/mangadex-full-api
# Thanks!
TITLES_PATTERN = re.compile(
    r"""<a[^>]*href=["']\/title\/(\d+)\/\S+["'][^>]*manga_title[^>]*>([^<]*)<"""
)


def _parse_chapter_number(string):
    if string == "":
        # most likely a oneshot
        return {"number": ""}
    nums = string.split(".")
    count = len(nums)
    assert count == 1 or count == 2
    result = {"number": string}
    result["num_major"] = int(nums[0])
    if count == 2:
        result["num_minor"] = int(nums[1])
    return result
