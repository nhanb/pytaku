import html
import re
import time

from mangoapi.base_site import Site, requires_login


class Mangadex(Site):
    def get_title(self, title_id):
        url = f"https://mangadex.org/api/?id={title_id}&type=manga"
        md_resp = self.http_get(url)
        md_json = md_resp.json()
        assert md_json["status"] == "OK"

        cover = md_json["manga"]["cover_url"].split("/")[-1]
        cover_ext = cover[cover.find(".") + 1 : cover.rfind("?")]

        current_timestamp = time.time()

        title = {
            "id": title_id,
            "name": md_json["manga"]["title"],
            "site": "mangadex",
            "cover_ext": cover_ext,
            "alt_names": md_json["manga"]["alt_names"],
            "descriptions": html.unescape(md_json["manga"]["description"]).split(
                "\r\n\r\n"
            ),
            "chapters": [
                {
                    "id": str(chap_id),
                    "name": chap["title"],
                    "volume": int(chap["volume"]) if chap["volume"] else None,
                    "groups": _extract_groups(chap),
                    **_parse_chapter_number(chap["chapter"]),
                }
                for chap_id, chap in md_json.get("chapter", {}).items()
                if chap["lang_code"] == "gb"
                and chap["group_name"] != "MangaPlus"
                and chap["timestamp"] <= current_timestamp
                # ^ Chapter may be listed but with access delayed for a certain amount
                # of time set by uploader, in which case we just filter it out. God I
                # hate this generation of Patreon "scanlators".
            ],
        }
        return title

    def get_chapter(self, title_id, chapter_id):
        md_resp = self.http_get(
            f"https://mangadex.org/api/?id={chapter_id}&type=chapter&saver=0"
        )
        md_json = md_resp.json()
        assert md_json["status"] == "OK"

        # 2 cases:
        # - If 'server_fallback' is absent, it means 'server' points to MD's own server
        #   e.g. s5.mangadex.org...
        # - Otherwise, 'server' points to a likely ephemeral MD@H node, while
        # 'server_fallback' now points to MD's own server.
        #
        # MD's own links apparently go dead sometimes, but MD@H links seem to expire
        # quickly all the time, so it's probably a good idea to store both anyway.

        server_fallback = md_json.get("server_fallback")
        if server_fallback:
            md_server = server_fallback
            mdah_server = md_json["server"]
        else:
            md_server = md_json["server"]
            mdah_server = None

        chapter = {
            "id": chapter_id,
            "title_id": str(md_json["manga_id"]),
            "site": "mangadex",
            "name": md_json["title"],
            "pages": [
                f"{md_server}{md_json['hash']}/{page}" for page in md_json["page_array"]
            ],
            "pages_alt": [
                f"{mdah_server}{md_json['hash']}/{page}"
                for page in md_json["page_array"]
            ]
            if mdah_server
            else [],
            "groups": _extract_groups(md_json),
            "is_webtoon": md_json["long_strip"] == 1,
            **_parse_chapter_number(md_json["chapter"]),
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


def _extract_groups(chap):
    return [
        html.unescape(group.strip())
        for group in [chap["group_name"], chap["group_name_2"], chap["group_name_3"]]
        if group
    ]
