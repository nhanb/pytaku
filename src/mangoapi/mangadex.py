import html
import re

import bbcode

from mangoapi.base_site import Site

MANGAPLUS_GROUP_ID = 9097
WEB_COMIC_TAG_ID = "e197df38-d0e7-43b5-9b09-2842d0c326dd"

_bbparser = bbcode.Parser()
_bbparser.add_simple_formatter(
    "spoiler", "<details><summary>Spoiler</summary>%(value)s</details>"
)


class Mangadex(Site):
    def get_title(self, title_id):
        md_resp = self.http_get(
            f"https://api.mangadex.org/manga/{title_id}",
            params={"includes[]": "cover_art"},
        )
        assert md_resp.status_code == 200
        md_json = md_resp.json()
        attrs = md_json["data"]["attributes"]

        is_web_comic = False
        for tag in attrs["tags"]:
            if tag["id"] == WEB_COMIC_TAG_ID:
                is_web_comic = True
                break

        cover = None
        for rel in md_json["data"]["relationships"]:
            if rel["type"] == "cover_art":
                cover = rel["attributes"]["fileName"]

        descriptions = attrs["description"]
        if not descriptions:
            description = ""
        elif "en" in descriptions:
            description = descriptions["en"]
        else:
            description = list(descriptions.values())[0]

        title = {
            "id": title_id,
            "name": list(attrs["title"].values())[0],
            "site": "mangadex",
            "cover_ext": cover,
            "alt_names": [list(alt.values())[0] for alt in attrs["altTitles"]],
            "descriptions": [_bbparser.format(html.unescape(description).strip())]
            if description
            else [],
            "descriptions_format": "html",
            "is_webtoon": is_web_comic,
            "chapters": self.get_chapters_list(title_id),
        }
        return title

    def get_chapters_list(self, title_id):
        resp = self.http_get(
            f"https://api.mangadex.org/manga/{title_id}/aggregate",
            params={"translatedLanguage[]": "en"},
        )
        assert resp.status_code == 200
        volumes: dict = resp.json()["volumes"]
        chapters = []

        # If there are no volumes, it's an empty list.
        # But if there are actual volumes, it's a dict.
        if type(volumes) is list:
            return []
        for vol in volumes.values():
            # Counting on python's spanking new key-order-preserving dicts here.
            # But WHY THE ACTUAL FUCK would you (mangadex) depend on JSON's key-value
            # pairs ordering?  A JSON object's keys is supposed to be unordered FFS.
            # If it actually becomes a problem I'll do chapter sorting later. Soon. Ish.
            chapters += (
                [
                    {
                        "id": chap["id"],
                        "name": "",
                        "groups": [],  # TODO
                        "volume": vol["volume"]
                        if vol["volume"] not in (None, "none")
                        else "",
                        **_parse_chapter_number(chap["chapter"]),
                    }
                    for chap in vol["chapters"].values()  # again, fucking yikes
                ]
                if type(vol["chapters"]) is dict
                else []
            )

        return chapters

    def get_chapter(self, title_id, chapter_id):
        md_resp = self.http_get(f"https://api.mangadex.org/chapter/{chapter_id}")
        assert md_resp.status_code == 200
        md_json = md_resp.json()
        data = md_json["data"]

        title_id = None
        for rel in data["relationships"]:
            if rel["type"] == "manga":
                title_id = rel["id"]
                break
        # chapter_hash = data["attributes"]["hash"]
        # filenames = data["attributes"]["data"]
        md_server = "https://uploads.mangadex.org"

        mdah_api_url = f"https://api.mangadex.org/at-home/server/{chapter_id}"
        mdah_resp = self.http_get(mdah_api_url)
        assert mdah_resp.status_code == 200, f"Failed request to {mdah_api_url}"
        mdah_data = mdah_resp.json()
        mdah_server = mdah_data["baseUrl"]
        chapter_hash = mdah_data["chapter"]["hash"]
        filenames = mdah_data["chapter"]["data"]

        chapter = {
            "id": chapter_id,
            "title_id": title_id,
            "site": "mangadex",
            "name": data["attributes"]["title"],
            "pages": [
                f"{md_server}/data/{chapter_hash}/{filename}" for filename in filenames
            ],
            "pages_alt": [
                f"{mdah_server}/data/{chapter_hash}/{filename}"
                for filename in filenames
            ]
            if mdah_server is not None and mdah_server != md_server
            else [],
            "groups": [],  # TODO
            **_parse_chapter_number(data["attributes"]["chapter"]),
        }
        return chapter

    def search_title(self, query):
        params = {
            "limit": 100,
            "title": query,
            "includes[]": "cover_art",
            "order[relevance]": "desc",
        }
        md_resp = self.http_get("https://api.mangadex.org/manga", params=params)
        assert md_resp.status_code == 200
        results = md_resp.json()["data"]

        titles = []
        for result in results:
            data = result
            cover = None
            for rel in result["relationships"]:
                if rel["type"] == "cover_art":
                    cover = rel["attributes"]["fileName"]
            titles.append(
                {
                    "id": data["id"],
                    "name": data["attributes"]["title"]["en"],
                    "site": "mangadex",
                    "thumbnail": f"https://uploads.mangadex.org/covers/{data['id']}/{cover}.256.jpg",
                }
            )

        return titles

    def title_cover(self, title_id, cover_ext):
        return f"https://uploads.mangadex.org/covers/{title_id}/{cover_ext}.256.jpg"

    def title_thumbnail(self, title_id, cover_ext):
        return f"https://uploads.mangadex.org/covers/{title_id}/{cover_ext}.256.jpg"

    def title_source_url(self, title_id):
        return f"https://mangadex.org/title/{title_id}"


# Titles regex slightly adapted from https://github.com/md-y/mangadex-full-api
# Thanks!
TITLES_PATTERN = re.compile(
    r"""<a[^>]*href=["']\/title\/(\d+)\/\S+["'][^>]*manga_title[^>]*>([^<]*)<"""
)


def _parse_chapter_number(string):
    if string in (None, "none"):
        # most likely a oneshot
        return {"number": "0.0", "num_major": 0, "num_minor": 0}
    nums = string.split(".")
    count = len(nums)
    assert count == 1 or count == 2
    result = {"number": string}
    result["num_major"] = int(nums[0])
    if count == 2:
        result["num_minor"] = int(nums[1])
    return result
