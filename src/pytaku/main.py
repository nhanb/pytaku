import base64
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from pathlib import Path
from typing import List, Tuple

import requests
from flask import Flask, jsonify, make_response, render_template, request, url_for

from .conf import config
from .decorators import handle_source_site_errors, process_token
from .persistence import (
    create_token,
    delete_token,
    follow,
    get_followed_titles,
    get_prev_next_chapters,
    get_username,
    import_follows,
    is_manga_page_url,
    load_chapter,
    load_title,
    read,
    register_user,
    save_chapter,
    save_title,
    unfollow,
    unread,
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
from .storages import storage

config.load()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=config.FLASK_SECRET_KEY,
    PERMANENT_SESSION_LIFETIME=timedelta(days=365),
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # max 10MiB payload
)


def _chapter_name(chapter: dict):
    result = ""
    if chapter.get("num_major") is not None:
        result += "Ch. " if chapter.get("volume") else "Chapter "
        result += str(chapter["num_major"])
    if chapter.get("num_minor"):
        result += '.{chapter["num_minor"]}'
    if chapter.get("volume"):
        result += f"Vol. {chapter['volume']}"
    if chapter.get("name"):
        result += f" - {chapter['name']}"
    return result


def _encode_proxy_url(url):
    return base64.urlsafe_b64encode(url.encode()).decode()


def _decode_proxy_url(b64_url):
    return base64.urlsafe_b64decode(b64_url).decode()


def _is_manga_img_url(
    url,
    cover_pattern=re.compile(r"^https://([\w-]+\.)?mangadex\.org/images"),
):
    """
    Check if either a cover or page img url.
    """
    # Mangasee has god knows how many domains for manga page images, so we can't just
    # do a regex check, but need to query our db instead.
    return cover_pattern.match(url) or is_manga_page_url(url)


def proxied(url) -> str:
    path = url_for("proxy_view", b64_url=_encode_proxy_url(url))
    return config.PROXY_PREFIX + path


@app.route("/proxy/<b64_url>")
def proxy_view(b64_url):
    """
    Cached proxy for images (manga cover/page). Motivations:
        - get around source site's hotlinking protection
        - keep working even when source site is down
        - be a polite netizen in general
    """
    url = _decode_proxy_url(b64_url)
    if not _is_manga_img_url(url):
        print("Invalid img url:", url)
        return "Nope", 400

    cached_file_path = Path(config.PROXY_CACHE_DIR) / b64_url
    cached_headers_path = cached_file_path.with_suffix(".headers.json")

    if not (storage.exists(cached_file_path) and storage.exists(cached_headers_path)):
        md_resp = requests.get(url)
        status_code = md_resp.status_code
        body = md_resp.content
        # Normal responsible adults would always include the Content-Type header,
        # but it's MangaDex@Home we're talking about so ofc they wouldn't.
        # Therefore, watch out for that empty case:
        content_type = md_resp.headers.get("content-type")
        headers = {"Content-Type": content_type} if content_type else {}
        if status_code == 200:
            storage.save(cached_headers_path, json.dumps(headers).encode())
            storage.save(cached_file_path, md_resp.content)
    else:
        status_code = 200
        body = storage.read(cached_file_path)
        headers = json.loads(storage.read(cached_headers_path))

    headers["Cache-Control"] = "max-age=31536000"

    return body, status_code, headers


def read_tachiyomi_follows(text: str) -> List[Tuple[str, str]]:
    try:
        data = json.loads(text)
        mangadex_id = None
        mangasee_id = None
        for extension in data["extensions"]:
            id, name = extension.split(":")
            if name == "MangaDex":
                mangadex_id = int(id)
            elif name == "Mangasee":
                mangasee_id = int(id)
        assert mangadex_id and mangasee_id

        results = []
        for manga in data["mangas"]:
            path = manga["manga"][0]
            site_id = manga["manga"][2]
            if site_id == mangadex_id:
                site = "mangadex"
                title_id = path[len("/manga/") : -1]
            elif site_id == mangasee_id:
                site = "mangasee"
                title_id = path[len("/manga/") :]
            else:
                continue
            results.append((site, title_id))

        return results

    except Exception:  # yikes
        import traceback

        traceback.print_exc()
        return None


def ensure_titles(site_title_pairs: List[Tuple[str, str]]):
    """
    Fetch and save titles that are not already in db.
    Returns a list of title dicts, both old and new.
    """
    title_dicts = []
    new_titles = []

    for site, title_id in site_title_pairs:
        existing_title = load_title(site, title_id)
        if existing_title is None:  # again, n+1 queries are fine in sqlite
            new_titles.append((site, title_id))
        else:
            title_dicts.append(existing_title)

    print(f"Fetching {len(new_titles)} new titles out of {len(site_title_pairs)}.")
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(get_title, site, title_id) for site, title_id in new_titles
        ]
        for future in as_completed(futures):
            title = future.result()
            save_title(title)
            print(f"Saved {title['site']}: {title['name']}")
            title_dicts.append(title)

    return title_dicts


@app.route("/")
@app.route("/h")
@app.route("/a")
@app.route("/f")
@app.route("/s")
@app.route("/s/<query>")
@app.route("/i")
def home_view(query=None):
    return render_template("spa.html")


def _title(site, title_id, user_id=None):
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
        title["cover"] = proxied(title["cover"])
    title["source_url"] = title_source_url(site, title_id)
    return title


@app.route("/m/<site>/<title_id>")
@handle_source_site_errors("html")
def spa_title_view(site, title_id):
    title = _title(site, title_id)
    return render_template(
        "spa.html",
        open_graph={
            "title": title["name"],
            "image": title["cover"],
            "description": "\n".join(title["descriptions"]),
        },
    )


@app.route("/m/<site>/<title_id>/<chapter_id>")
@handle_source_site_errors("html")
def spa_chapter_view(site, title_id, chapter_id):
    chapter = load_chapter(site, title_id, chapter_id)
    if not chapter:
        print("Getting chapter", chapter_id)
        chapter = get_chapter(site, title_id, chapter_id)
        save_chapter(chapter)
    else:
        print("Loading chapter", chapter_id, "from db")

    # YIIIIKES
    title = load_title(site, title_id)
    title["cover"] = title_cover(site, title_id, title["cover_ext"])
    if site == "mangadex":
        title["cover"] = proxied(title["cover"])

    chapter["site"] = site
    return render_template(
        "spa.html",
        open_graph={
            "title": f'{_chapter_name(chapter)} - {title["name"]}',
            "image": title["cover"],
            "description": "\n".join(title["descriptions"]),
        },
    )


@app.route("/api/title/<site>/<title_id>", methods=["GET"])
@process_token(required=False)
@handle_source_site_errors("json")
def api_title(site, title_id):
    title = _title(site, title_id, user_id=request.user_id)
    return title


@app.route("/api/chapter/<site>/<title_id>/<chapter_id>", methods=["GET"])
@process_token(required=False)
@handle_source_site_errors("json")
def api_chapter(site, title_id, chapter_id):
    chapter = load_chapter(site, title_id, chapter_id)
    if not chapter:
        print("Getting chapter", chapter_id)
        chapter = get_chapter(site, title_id, chapter_id)
        save_chapter(chapter)
    else:
        print("Loading chapter", chapter_id, "from db")

    if site in ("mangadex", "mangasee"):
        chapter["pages"] = [proxied(p) for p in chapter["pages"]]
        chapter["pages_alt"] = [proxied(p) for p in chapter["pages_alt"]]

    # YIIIIKES
    title = load_title(site, title_id)
    title["cover"] = title_cover(site, title_id, title["cover_ext"])
    if site == "mangadex":
        title["cover"] = proxied(title["cover"])
    prev_chapter, next_chapter = get_prev_next_chapters(title, chapter)
    chapter["prev_chapter"] = prev_chapter
    chapter["next_chapter"] = next_chapter
    chapter["site"] = site
    return chapter


@app.route("/api/register", methods=["POST"])
def api_register():
    username = request.json["username"].strip()
    password = request.json["password"]
    message = None
    if not (username and password):
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
            message = "Registration successful! You can login now."
            status_code = 200
    return (jsonify({"message": message}), status_code)


@app.route("/api/login", methods=["POST"])
def api_login():
    username = request.json["username"].strip()
    password = request.json["password"]
    remember = request.json["remember"]

    if not (username and password):
        return (
            jsonify({"message": "Empty field(s) spotted. Protip: spaces don't count."}),
            400,
        )

    user_id = verify_username_password(username, password)
    if not user_id:
        return jsonify({"message": "Wrong username/password combination."}), 401

    token = create_token(user_id, remember)
    resp = make_response(jsonify({"user_id": user_id, "token": token}))
    resp.set_cookie(
        "token", token, max_age=31536000 if remember else None, samesite="Strict"
    )
    return resp


@app.route("/api/verify-token", methods=["GET"])
@process_token(required=True)
def api_verify_token():
    return {"user_id": request.user_id, "username": get_username(request.user_id)}, 200


@app.route("/api/logout", methods=["POST"])
@process_token(required=True)
def api_logout():
    num_deleted = delete_token(request.token)
    if num_deleted != 1:
        return jsonify({"message": "Invalid token."}), 401
    resp = make_response("{}", 200)
    resp.set_cookie("token", "", expires=0, samesite="Strict")
    return resp


@app.route("/api/follows", methods=["GET"])
@process_token(required=True)
def api_follows():
    titles = get_followed_titles(request.user_id)
    for title in titles:
        thumbnail = title_thumbnail(title["site"], title["id"])
        if title["site"] == "mangadex":
            thumbnail = proxied(thumbnail)
        title["thumbnail"] = thumbnail
    return jsonify({"titles": titles})


@app.route("/api/search/<query>", methods=["GET"])
def api_search(query):
    results = search_title_all_sites(query)

    if "mangadex" in results:
        for title in results["mangadex"]:
            title["thumbnail"] = proxied(title["thumbnail"])
    return results


@app.route("/api/follow", methods=["POST"])
@process_token(required=True)
@handle_source_site_errors("json")
def api_follow():
    should_follow = request.json["follow"]
    site = request.json["site"]
    title_id = request.json["title_id"]

    if should_follow:
        follow(request.user_id, site, title_id)
    else:
        unfollow(request.user_id, site, title_id)

    return jsonify({"follow": should_follow})


@app.route("/api/read", methods=["POST"])
@process_token(required=True)
def api_read():
    reads = request.json.get("read") or []
    unreads = request.json.get("unread") or []
    assert reads or unreads

    if reads:
        for r in reads:
            read(
                request.user_id,
                r["site"],
                r["title_id"],
                r["chapter_id"],
            )
    if unreads:
        for u in unreads:
            unread(
                request.user_id,
                u["site"],
                u["title_id"],
                u["chapter_id"],
            )
    # TODO: rewrite read/unread to do bulk updates instead of n+1 queries like these.
    # ... Or maybe not. SQLite doesn't mind.

    # Also TODO: maybe a separate "read all from title" API would be cleaner & easier on
    # FE side.
    return {}


@app.route("/api/import", methods=["POST"])
@process_token(required=True)
@handle_source_site_errors("json")
def api_import():
    # check if the post request has the file part
    if "tachiyomi" not in request.files:
        return jsonify({"message": "No file provided"}), 400
    file = request.files["tachiyomi"]

    # if user does not select file, browser also
    # submits an empty part without filename
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    if file:
        text = file.read()
        site_title_pairs = read_tachiyomi_follows(text)
        if site_title_pairs is None:
            return jsonify({"message": "Malformed file."}), 400

        # First fetch & save titles if they're not already in db
        titles = ensure_titles(site_title_pairs)

        # Then follow them all
        import_follows(request.user_id, site_title_pairs)

        # Mark all chapters as read too
        for title in titles:
            for chapter in title["chapters"]:
                read(request.user_id, title["site"], title["id"], chapter["id"])

        return jsonify({"message": f"Added {len(site_title_pairs)} follows."})
