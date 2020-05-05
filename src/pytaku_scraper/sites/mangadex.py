import itertools
import re

import requests
from attr import attrib, attrs
from bs4 import BeautifulSoup

DOMAIN = "https://mangadex.org"
API_URL = "https://mangadex.org/api/"

session = requests.Session()
session.headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
}


@attrs(slots=True, kw_only=True)
class Title(object):
    url = attrib(type=str)
    name = attrib(type=str)
    alt_names = attrib(type=list)
    authors = attrib(type=list)
    tags = attrib(type=list)
    publication_status = attrib(type=str)
    descriptions = attrib(type=list)
    chapters = attrib(type=list)


@attrs(slots=True, kw_only=True)
class Chapter(object):
    name = attrib(type=str)
    pages = attrib(type=list)


def title_url_from_id(original_id):
    return f"{DOMAIN}/title/{original_id}"


def chapter_url_from_id(original_id):
    return f"{DOMAIN}/chapter/{original_id}"


_chapter_url_regex = re.compile("^" + DOMAIN + r"/chapter/(\d+)/?$")


def chapter_id_from_url(url):
    match = _chapter_url_regex.match(url)
    return match.group(1) if match else None


_title_url_regex = re.compile("^" + DOMAIN + r"/title/(\d+)(/.*)?$")


def title_id_from_url(url):
    match = _title_url_regex.match(url)
    return match.group(1) if match else None


def scrape_title(original_id):
    source_url = title_url_from_id(original_id)
    html = session.get(source_url).text
    soup = BeautifulSoup(html, "lxml")
    print(soup)

    url = soup.select('link[rel="canonical"]')[0].attrs["href"]
    name = soup.select(".card-header span.mx-1")[0].text

    alt_names = _get_next_column_of(soup, "Alt name(s)", "li")
    authors = _get_next_column_of(soup, "Author", "a")
    artists = _get_next_column_of(soup, "Artist", "a")
    genres = _get_next_column_of(soup, "Genre", "a")
    themes = _get_next_column_of(soup, "Theme", "a")
    pub_status = _get_next_column_of(soup, "Pub. status")

    raw_descs = _get_next_column_of(soup, "Description")
    descriptions = [desc.strip() for desc in raw_descs.split("\n\n") if desc.strip()]

    chapters = _get_chapters(soup)
    return {
        "url": url,
        "name": name,
        "alt_names": alt_names,
        "authors": sorted(set(authors + artists)),
        "tags": sorted(set(genres + themes)),
        "publication_status": pub_status,
        "descriptions": descriptions,
        "chapters": chapters,
    }


def _get_next_column_of(soup, query, subtag=None):
    label = soup.find("div", string=f"{query}:")
    if label is None:
        return None if subtag is None else []

    # newlines also count as sibling, so we have to filter them out:
    siblings = [sibl for sibl in label.next_siblings if sibl.name is not None]
    if len(siblings) != 1:
        raise Exception(f'Unexpected siblings found for "{query}": {siblings}')
    next_column = siblings[0]
    return _get_column_content(next_column, subtag)


def _get_column_content(column, subtag):
    if subtag is None:
        return column.text.strip()
    else:
        return [
            child.text.strip()
            for child in column.find_all(subtag)
            if child.text.strip()
        ]


def _get_chapters(soup):
    chapter_page_urls = _chapter_page_urls(soup)
    chapter_page_soups = [
        BeautifulSoup(session.get(f"{DOMAIN}{url}").text, "lxml")
        for url in chapter_page_urls
    ]
    chapter_page_soups.insert(0, soup)  # saves us 1 http request :)
    chapters = [_chapters_data(soup) for soup in chapter_page_soups]
    return list(itertools.chain(*chapters))  # flatten list of list


def _chapter_page_urls(soup):
    """
    Excluding first page because we already have it
    """
    last_chapter_link_tag = soup.find(title="Jump to last page")
    if not last_chapter_link_tag:
        return []

    last_chapter_link = last_chapter_link_tag.parent.attrs["href"]
    if last_chapter_link[-1] == "/":
        last_chapter_link = last_chapter_link[:-1]

    parts = last_chapter_link.split("/")
    max_page = int(parts.pop())

    template = "/".join(parts + ["%d/"])

    return [template % page_num for page_num in range(2, max_page + 1)]


def _chapters_data(soup):
    chapter_container = soup.find(class_="chapter-container")

    def is_chapter_link(href):
        return href.startswith("/chapter/") and not href.endswith("comments")

    chapters = chapter_container.find_all("a", href=is_chapter_link)

    eng_chapters = [
        {
            "id": chapter_id_from_url(f'{DOMAIN}{chapter.attrs["href"]}'),
            "name": chapter.text,
        }
        for chapter in chapters
        if chapter.parent.parent.find(class_="flag", title="English")
    ]
    return eng_chapters


def scrape_chapter(original_id):
    data = session.get(API_URL, params={"id": original_id, "type": "chapter"}).json()

    if data["status"] == "deleted":
        return None

    # data["server"] can be either of:
    # - "/data/..." - meaning same origin as web server: https://mangadex.org/data/...
    # - "https://sX.mangadex.org/data/..." where X is any digit.
    page_base_url = data["server"] + data["hash"]
    if page_base_url.startswith("/"):
        page_base_url = f"https://mangadex.org{page_base_url}"
    pages = [f"{page_base_url}/{page}" for page in data["page_array"]]

    return {
        "name": data["title"],
        "pages": pages,
    }
