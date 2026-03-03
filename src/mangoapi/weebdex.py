from mangoapi.base_site import Site


class Weebdex(Site):
    search_table = None

    def __init__(self, keyval_store=None):
        super().__init__()
        self.keyval_store = keyval_store

    def get_title(self, title_id):
        title = self.http_get(f"https://api.weebdex.org/manga/{title_id}").json()

        limit = 500
        chapters = []
        page = 0

        while True:
            page += 1
            chaps = self.http_get(
                f"https://api.weebdex.org/manga/{title_id}/chapters",
                params={
                    "limit": limit,
                    "tlang": "en",
                    "page": page,
                },
            ).json()

            chapters += [
                {
                    "groups": [],
                    "id": chap["id"],
                    "name": chap.get("title", ""),
                    "volume": chap["volume"],
                    **_parse_chapter_number(chap.get("chapter", "0")),
                }
                for chap in chaps["data"]
            ]

            if len(chapters) >= chaps["total"]:
                break

        descriptions = (
            title.get("description", "").split("\n\n")
            if title.get("description")
            else []
        )

        return {
            "id": title_id,
            "name": title["title"],
            "site": "weebdex",
            "cover_ext": title["relationships"]["cover"]["id"],
            "is_webtoon": False,
            "chapters": chapters,
            "alt_names": [],
            "descriptions": descriptions,
            "descriptions_format": "text",
        }

    def get_chapter(self, title_id, chapter_id):
        chapter = self.http_get(f"https://api.weebdex.org/chapter/{chapter_id}").json()

        node = chapter["node"]
        pages = [f"{node}/data/{chapter_id}/{page['name']}" for page in chapter["data"]]

        result = {
            "id": chapter_id,
            "title_id": title_id,
            "site": "weebdex",
            "name": chapter.get("title"),
            "pages": pages,
            "pages_alt": [],
            "groups": [],
            **_parse_chapter_number(chapter.get("chapter", "0")),
        }
        return result

    def search_title(self, query):
        titles = self.http_get(
            "https://api.weebdex.org/manga",
            params={"title": query, "sort": "relevance"},
        ).json()["data"]

        return [
            {
                "id": title["id"],
                "name": title["title"],
                "site": "weebdex",
                "thumbnail": self.title_thumbnail(
                    title["id"],
                    title["relationships"]["cover"]["id"],
                ),
            }
            for title in titles
        ]

    # I'm cheating a little here - cover_ext is actually the cover image ID.

    def title_cover(self, title_id, cover_ext):
        return f"https://weebdex.org/covers/{title_id}/{cover_ext}.512.webp"

    def title_thumbnail(self, title_id, cover_ext):
        return f"https://weebdex.org/covers/{title_id}/{cover_ext}.256.webp"

    def title_source_url(self, title_id):
        return f"https://weebdex.org/title/{title_id}/"


def _parse_chapter_number(string: str):
    if string in (None, "none"):
        # most likely a oneshot
        return {"number": "0.0", "num_major": 0, "num_minor": 0}
    nums = string.split(".", maxsplit=1)
    result = {"number": string}
    result["num_major"] = nums[0]
    if len(nums) == 2:
        result["num_minor"] = nums[1]
    return result
