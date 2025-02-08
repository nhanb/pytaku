import re
from html import unescape

from mangoapi.base_site import Site

regexes = {
    "title_name": re.compile(r"<title>\s*([^|]+) | Weeb Central</title>"),
    "title_chapters": re.compile(
        r'a href="https:\/\/weebcentral.com\/chapters\/([A-Z0-9]+)"(.|\n)+?\>Chapter (([0-9]+)(\.([0-9])+)?)\<'
    ),
    "title_desc": re.compile(r"<strong>Description<\/strong>\w*[^<]+<p[^>]*>([^<]+)<"),
    "chapter_number": re.compile(r"<span>Chapter (([0-9]+)(\.([0-9]+))?)</span>"),
    "chapter_imgs": re.compile(r'<img\s+src="(https?://.*?)"'),
    "search_data": re.compile(
        r'<a href="https://weebcentral.com/series/([A-Z0-9]+)/(\n|.)+?alt="(.+?) cover"'
    ),
}


class Weebcentral(Site):
    search_table = None

    def __init__(self, keyval_store=None):
        super().__init__()
        self.keyval_store = keyval_store

    def get_title(self, title_id):
        resp = self.http_get(f"https://weebcentral.com/series/{title_id}")
        html = resp.text
        name = unescape(regexes["title_name"].search(html).group(1)).strip()
        desc = unescape(regexes["title_desc"].search(html).group(1)).strip()
        chapters_html = self.http_get(
            f"https://weebcentral.com/series/{title_id}/full-chapter-list"
        ).text

        chapters = [
            {
                "id": chap_id,
                "name": "",
                "volume": "",
                "groups": [],
                "num_major": int(num_major),
                "num_minor": int(num_minor) if num_minor else 0,
                "number": number,
            }
            for chap_id, _, number, num_major, _, num_minor in regexes[
                "title_chapters"
            ].findall(chapters_html)
        ]

        return {
            "id": title_id,
            "name": name,
            "site": "weebcentral",
            "cover_ext": "webp",
            "is_webtoon": False,
            "chapters": chapters,
            "alt_names": [],
            "descriptions": [desc],
            "descriptions_format": "text",
        }

    def get_chapter(self, title_id, chapter_id):
        html = self.http_get(f"https://weebcentral.com/chapters/{chapter_id}").text
        number, num_major, _, num_minor = (
            regexes["chapter_number"].search(html).groups()
        )

        imgs_html = self.http_get(
            f"https://weebcentral.com/chapters/{chapter_id}/images?is_prev=False&current_page=1&reading_style=long_strip"
        ).text
        pages = regexes["chapter_imgs"].findall(imgs_html)

        result = {
            "id": chapter_id,
            "title_id": title_id,
            "site": "weebcentral",
            "name": "",
            "pages": pages,
            "pages_alt": [],
            "groups": [],
            "num_major": int(num_major),
            "num_minor": int(num_minor) if num_minor else 0,
            "number": number,
        }
        return result

    def search_title(self, query):
        html = self.http_post(
            "https://weebcentral.com/search/simple?location=main",
            data={"text": query},
        ).text

        return [
            {
                "id": title_id,
                "name": unescape(name),
                "site": "weebcentral",
                "thumbnail": self.title_thumbnail(title_id, "webp"),
            }
            for title_id, _, name in regexes["search_data"].findall(html)
        ]

    def title_cover(self, title_id, cover_ext):
        return self.title_thumbnail(title_id, cover_ext)

    def title_thumbnail(self, title_id, cover_ext):
        return f"https://temp.compsci88.com/cover/normal/{title_id}.webp"

    def title_source_url(self, title_id):
        return f"https://weebcentral.com/series/{title_id}"
