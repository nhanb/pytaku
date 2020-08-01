import base64
import re

import requests
from flask import Flask, make_response, render_template, url_for

from mangoapi import get_chapter, get_title

app = Flask(__name__)


@app.route("/")
def home_view():
    return render_template("home.html")


@app.route("/title/mangadex/<int:title_id>")
def title_view(title_id):
    title = get_title(title_id)
    return render_template("title.html", id=title_id, **title)


@app.route("/chapter/mangadex/<int:chapter_id>")
def chapter_view(chapter_id):
    chapter = get_chapter(chapter_id)
    chapter["pages"] = [
        url_for("proxy_view", b64_url=_encode_proxy_url(p)) for p in chapter["pages"]
    ]
    return render_template("chapter.html", **chapter)


@app.route("/search")
def search_view():
    return "TODO"


@app.route("/proxy/<b64_url>")
def proxy_view(b64_url):
    """Fine I'll do it"""
    url = _decode_proxy_url(b64_url)
    if not _is_manga_img_url(url):
        return "Nope"
    print("Proxying", url)
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
