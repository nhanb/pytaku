from flask import Flask, render_template

from mangoapi import get_chapter, get_title

app = Flask(__name__)


@app.route("/title/mangadex/<int:title_id>")
def title_view(title_id):
    title = get_title(title_id)
    return render_template("title.html", **title)


@app.route("/chapter/mangadex/<int:chapter_id>")
def chapter_view(chapter_id):
    chapter = get_chapter(chapter_id)
    return render_template("chapter.html", **chapter)


@app.route("/search")
def search_view():
    return "TODO"
