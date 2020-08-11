import base64
import re
from datetime import timedelta

import requests
from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .conf import config
from .decorators import require_login, toggle_has_read
from .persistence import (
    follow,
    get_followed_titles,
    get_prev_next_chapters,
    load_chapter,
    load_title,
    register_user,
    save_chapter,
    save_title,
    unfollow,
    verify_username_password,
)
from .source_sites import (
    get_chapter,
    get_title,
    search_title_all_sites,
    title_cover,
    title_source_url,
    title_thumbnail,
)

config.load()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=config.FLASK_SECRET_KEY, PERMANENT_SESSION_LIFETIME=timedelta(days=365),
)


@app.route("/")
def home_view():
    if session.get("user"):
        return redirect(url_for("follows_view"))
    return render_template("home.html")


@app.route("/following", methods=["GET"])
@require_login
def follows_view():
    titles = get_followed_titles(session["user"]["id"])
    for title in titles:
        thumbnail = title_thumbnail(title["site"], title["id"])
        if title["site"] == "mangadex":
            thumbnail = url_for("proxy_view", b64_url=_encode_proxy_url(thumbnail))
        title["thumbnail"] = thumbnail
    return render_template("follows.html", titles=titles)


@app.route("/follow/<site>/<title_id>", methods=["POST"])
@require_login
def follow_view(site, title_id):
    follow(session["user"]["id"], site, title_id)
    return redirect(url_for("title_view", site=site, title_id=title_id))


@app.route("/unfollow/<site>/<title_id>", methods=["POST"])
@require_login
def unfollow_view(site, title_id):
    unfollow(session["user"]["id"], site, title_id)
    return redirect(url_for("title_view", site=site, title_id=title_id))


@app.route("/logout", methods=["POST"])
def logout_view():
    session.pop("user")
    return redirect("/")


@app.route("/auth", methods=["GET", "POST"])
def auth_view():
    if session.get("user"):
        return redirect(url_for("home_view"))

    if request.method == "POST":

        if request.form["action"] == "register":
            username = request.form["username"].strip()
            password = request.form["password"]
            confirm_password = request.form["confirm-password"]
            message = None
            if password != confirm_password:
                message = "Password confirmation didn't match."
                status_code = 400
            elif not (username and password and confirm_password):
                message = "Empty field(s) spotted. Protip: spaces don't count."
                status_code = 400
            elif (
                len(username) < 2
                or len(username) > 15
                or len(password) < 5
                or len(password) > 50
            ):
                message = "Invalid username/password length. Username length should be 2~15, password 5~50."
                status_code = 400
            else:  # success!
                err = register_user(username, password)
                if err:
                    message = err
                    status_code = 400
                else:
                    username = ""
                    password = ""
                    confirm_password = ""
                    message = "Registration successful! You can login now."
                    status_code = 200
            return (
                render_template(
                    "auth.html",
                    register_username=username,
                    register_password=password,
                    register_confirm_password=confirm_password,
                    register_message=message,
                    register_has_error=status_code != 200,
                ),
                status_code,
            )

        else:  # action == 'login'
            username = request.form["username"].strip()
            password = request.form["password"]
            remember = request.form.get("remember") == "on"
            if not (username and password):
                message = "Empty field(s) spotted. Protip: spaces don't count."
                status_code = 400
            else:
                user_id = verify_username_password(username, password)
                if user_id is None:
                    message = "Wrong username/password combination."
                    status_code = 400
                else:  # success!
                    resp = redirect(request.args.get("next", url_for("home_view")))
                    session.permanent = remember
                    session["user"] = {"username": username, "id": user_id}
                    return resp

            return (
                render_template(
                    "auth.html",
                    login_username=username,
                    login_password=password,
                    login_remember=remember,
                    login_message=message,
                    login_has_error=status_code != 200,
                ),
                status_code,
            )

    # Just a plain ol' GET request:
    return render_template("auth.html")


@app.route("/m/<site>/<title_id>")
@toggle_has_read
def title_view(site, title_id):
    user = session.get("user", None)
    user_id = user["id"] if user else None
    title = load_title(site, title_id, user_id=user_id)
    if not title:
        print("Getting title", title_id)
        title = get_title(site, title_id)
        print("Saving title", title_id, "to db")
        save_title(title)
    else:
        print("Loading title", title_id, "from db")
    title["cover"] = title_cover(site, title_id, title["cover_ext"])
    if site == "mangadex":
        title["cover"] = url_for(
            "proxy_view", b64_url=_encode_proxy_url(title["cover"])
        )
    title["source_url"] = title_source_url(site, title_id)
    return render_template("title.html", **title)


@app.route("/m/<site>/<title_id>/<chapter_id>")
@toggle_has_read
def chapter_view(site, title_id, chapter_id):
    chapter = load_chapter(site, title_id, chapter_id)
    if not chapter:
        print("Getting chapter", chapter_id)
        chapter = get_chapter(site, title_id, chapter_id)
        chapter["site"] = site
        save_chapter(chapter)
    else:
        print("Loading chapter", chapter_id, "from db")

    if site in ("mangadex", "mangasee"):
        chapter["pages"] = [
            url_for("proxy_view", b64_url=_encode_proxy_url(p))
            for p in chapter["pages"]
        ]

    # YIIIIKES
    title = load_title(site, title_id)
    prev_chapter, next_chapter = get_prev_next_chapters(title, chapter)
    chapter["prev_chapter"] = prev_chapter
    chapter["next_chapter"] = next_chapter

    chapter["site"] = site
    return render_template("chapter.html", **chapter)


@app.route("/search")
def search_view():
    query = request.args.get("q", "").strip()
    results = {}
    if query:
        results = search_title_all_sites(query)

    if "mangadex" in results:
        for title in results["mangadex"]:
            title["thumbnail"] = url_for(
                "proxy_view", b64_url=_encode_proxy_url(title["thumbnail"])
            )
    return render_template("search.html", results=results, query=query)


@app.route("/proxy/<b64_url>")
def proxy_view(b64_url):
    """Fine I'll do it"""
    url = _decode_proxy_url(b64_url)
    if not _is_manga_img_url(url):
        print("Invalid img url:", url)
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
    url,
    pattern=re.compile(
        r"^https://([\w_-]+\.)?(mangadex\.org/(data|images)|mangabeast\d{0,4}.com/manga)/"
    ),
):
    return pattern.match(url)
