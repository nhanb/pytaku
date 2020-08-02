import base64
import re

import requests
from flask import Flask, make_response, render_template, request, url_for

from mangoapi import get_chapter, get_title, search_title

from . import mangadex
from .persistence import (
    get_prev_next_chapters,
    load_chapter,
    load_title,
    save_chapter,
    save_title,
)

app = Flask(__name__)


@app.route("/")
def home_view():
    return render_template("home.html")


@app.route("/title/mangadex/<title_id>")
def title_view(title_id):
    title = load_title(title_id)
    if not title:
        print("Getting title", title_id)
        title = get_title(title_id)
        print("Saving title", title_id, "to db")
        save_title(title)
    else:
        print("Loading title", title_id, "from db")
    return render_template("title.html", **title)


@app.route("/chapter/mangadex/<chapter_id>")
def chapter_view(chapter_id):
    chapter = load_chapter(chapter_id)
    if not chapter:
        print("Getting chapter", chapter_id)
        chapter = get_chapter(chapter_id)
        save_chapter(chapter)
    else:
        print("Loading chapter", chapter_id, "from db")

    chapter["pages"] = [
        url_for("proxy_view", b64_url=_encode_proxy_url(p)) for p in chapter["pages"]
    ]

    # YIIIIKES
    title = load_title(chapter["title_id"])
    prev_chapter, next_chapter = get_prev_next_chapters(title, chapter)
    chapter["prev_chapter"] = prev_chapter
    chapter["next_chapter"] = next_chapter

    return render_template("chapter.html", **chapter)


@app.route("/search")
def search_view():
    query = request.args.get("q", "").strip()
    titles = []
    if query:
        cookies = mangadex.get_cookies()
        titles = search_title(cookies, query)
    return render_template("search.html", titles=titles, query=query)


@app.route("/proxy/<b64_url>")
def proxy_view(b64_url):
    """Fine I'll do it"""
    url = _decode_proxy_url(b64_url)
    if not _is_manga_img_url(url):
        return "Nope", 400
    md_resp = requests.get(url)
    resp = make_response(md_resp.content, md_resp.status_code)
    resp.headers.extend(**md_resp.headers)
    return resp


def _encode_proxy_url(url):
    return base64.urlsafe_b64encode(url.encode()).decode()


def _decode_proxy_url(b64_url):
    return base64.urlsafe_b64decode(b64_url).decode()


def _is_manga_img_url(
    url, pattern=re.compile(r"^https://(\w+\.)?mangadex\.org/data/.+$")
):
    return pattern.match(url)
