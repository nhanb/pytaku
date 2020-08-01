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
        url_for("proxy_view", b64_url=base64.urlsafe_b64encode(p.encode()).decode())
        for p in chapter["pages"]
    ]
    return render_template("chapter.html", **chapter)


@app.route("/search")
def search_view():
    return "TODO"


@app.route("/proxy/<b64_url>")
def proxy_view(b64_url):
    """Fine I'll do it"""
    url = base64.urlsafe_b64decode(b64_url).decode()
    if not re.match(r"^https://\w+\.mangadex\.org/data/.+$", url):
        return "Nope"
    print("Proxying", url)
    md_resp = requests.get(url)
    resp = make_response(md_resp.content, md_resp.status_code)
    resp.headers.extend(**md_resp.headers)
    return resp
