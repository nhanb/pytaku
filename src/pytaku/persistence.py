import json
import secrets
from typing import List, Tuple

import apsw
import argon2

from .database.common import run_sql, run_sql_many


def save_title(title):
    run_sql(
        """
    INSERT INTO title (
        id,
        name,
        site,
        cover_ext,
        chapters,
        alt_names,
        descriptions
    ) VALUES (
        :id,
        :name,
        :site,
        :cover_ext,
        :chapters,
        :alt_names,
        :descriptions
    ) ON CONFLICT (id, site) DO UPDATE SET
        name=excluded.name,
        cover_ext=excluded.cover_ext,
        chapters=excluded.chapters,
        alt_names=excluded.alt_names,
        descriptions=excluded.descriptions,
        updated_at=datetime('now')
    ;
    """,
        {
            "id": title["id"],
            "name": title["name"],
            "site": title["site"],
            "cover_ext": title["cover_ext"],
            "chapters": json.dumps(title["chapters"]),
            "alt_names": json.dumps(title["alt_names"]),
            "descriptions": json.dumps(title["descriptions"]),
        },
    )


def load_title(site, title_id, user_id=None):
    result = run_sql(
        """
        SELECT id, name, site, cover_ext, chapters, alt_names, descriptions
        FROM title
        WHERE id = ?
          AND site = ?;
        """,
        (title_id, site),
    )
    if not result:
        return None
    elif len(result) > 1:
        raise Exception(f"Found multiple results for title_id {title_id} on {site}!")
    else:
        title = result[0]

        for field in ["chapters", "alt_names", "descriptions"]:
            title[field] = json.loads(title[field])

        if user_id is not None:
            title["is_following"] = bool(
                run_sql(
                    "SELECT 1 FROM follow WHERE user_id=? AND site=? AND title_id=?;",
                    (user_id, site, title["id"]),
                )
            )

            chapters_i_read = run_sql(
                """
                SELECT r.chapter_id
                FROM read r
                WHERE r.user_id = ?
                  AND r.title_id = ?
                  AND r.site = ?
                ORDER BY r.updated_at;
                """,
                (user_id, title["id"], title["site"]),
            )

            for ch in title["chapters"]:
                if ch["id"] in chapters_i_read:
                    ch["is_read"] = True
        return title


def save_chapter(chapter):
    run_sql(
        """
    INSERT INTO chapter (
        id,
        title_id,
        site,
        num_major,
        num_minor,
        name,
        pages,
        pages_alt,
        groups,
        is_webtoon
    ) VALUES (
        :id,
        :title_id,
        :site,
        :num_major,
        :num_minor,
        :name,
        :pages,
        :pages_alt,
        :groups,
        :is_webtoon
    ) ON CONFLICT (id, title_id, site) DO UPDATE SET
        num_major=excluded.num_major,
        num_minor=excluded.num_minor,
        name=excluded.name,
        pages=excluded.pages,
        pages_alt=excluded.pages_alt,
        groups=excluded.groups,
        is_webtoon=excluded.is_webtoon,
        updated_at=datetime('now')
    ;
    """,
        {
            "id": chapter["id"],
            "title_id": chapter["title_id"],
            "site": chapter["site"],
            "num_major": chapter.get("num_major"),
            "num_minor": chapter.get("num_minor"),
            "name": chapter["name"],
            "pages": json.dumps(chapter["pages"]),
            "pages_alt": json.dumps(chapter["pages_alt"]),
            "groups": json.dumps(chapter["groups"]),
            "is_webtoon": chapter["is_webtoon"],
        },
    )


def load_chapter(site, title_id, chapter_id, ignore_old=True):
    updated_at = "datetime('now', '-1 days')" if ignore_old else "'1980-01-01'"
    result = run_sql(
        f"""
        SELECT id, title_id, site, num_major, num_minor, name, pages, pages_alt, groups, is_webtoon
        FROM chapter
        WHERE site=? AND title_id=? AND id=? AND updated_at > {updated_at};
        """,
        (site, title_id, chapter_id),
    )
    if not result:
        return None
    elif len(result) > 1:
        raise Exception(f"Found multiple results for chapter_id {chapter_id}!")
    else:
        chapter = result[0]
        chapter["pages"] = json.loads(chapter["pages"])
        chapter["pages_alt"] = json.loads(chapter["pages_alt"])
        chapter["groups"] = json.loads(chapter["groups"])
        return chapter


def get_prev_next_chapters(title, chapter):
    """
    Maybe consider writing SQL query instead?
    """
    chapters = title["chapters"]
    chapter_id = chapter["id"]

    prev_chapter = None
    next_chapter = None
    for i, chap in enumerate(chapters):
        if chap["id"] == chapter_id:
            if i - 1 >= 0:
                next_chapter = chapters[i - 1]
            if i + 1 < len(chapters):
                prev_chapter = chapters[i + 1]

    return prev_chapter, next_chapter


def register_user(username, password):
    hasher = argon2.PasswordHasher()
    hashed_password = hasher.hash(password)
    try:
        run_sql(
            "INSERT INTO user (username, password) VALUES (?, ?);",
            (username, hashed_password),
        )
        return None
    except apsw.ConstraintError as e:
        if "UNIQUE" in str(e):
            return "Username already exists."
        raise


def verify_username_password(username, password):
    data = run_sql("SELECT id, password FROM user WHERE username = ?;", (username,))
    if len(data) != 1:
        print(f"User {username} doesn't exist.")
        return None

    user_id = data[0]["id"]
    hashed_password = data[0]["password"]
    hasher = argon2.PasswordHasher()
    try:
        hasher.verify(hashed_password, password)
        return user_id
    except argon2.exceptions.VerifyMismatchError:
        print(f"User {username} exists but password doesn't match.")
        return None


def follow(user_id, site, title_id):
    run_sql(
        """
        INSERT INTO follow (user_id, site, title_id) VALUES (?, ?, ?)
        ON CONFLICT DO NOTHING;
        """,
        (user_id, site, title_id),
    )


def unfollow(user_id, site, title_id):
    run_sql(
        "DELETE FROM follow WHERE user_id=? AND site=? AND title_id=?;",
        (user_id, site, title_id),
    )


def get_followed_titles(user_id):
    titles = run_sql(
        """
        SELECT t.id, t.site, t.name, t.cover_ext, t.chapters
        FROM title t
          INNER JOIN follow f ON f.title_id = t.id AND f.site = t.site
          INNER JOIN user u ON u.id = f.user_id
        WHERE user_id=?;
        """,
        (user_id,),
    )

    for t in titles:
        chapters = json.loads(t["chapters"])

        # n+1 queries cuz I don't give a f- actually I do, but sqlite's cool with it:
        # https://www.sqlite.org/np1queryprob.html
        chapters_i_finished = run_sql(
            """
            SELECT chapter_id
            FROM read
            WHERE user_id = ?
              AND title_id = ?
              AND site = ?;
            """,
            (user_id, t["id"], t["site"]),
        )
        # Only show chapters that user hasn't read
        chapters = [ch for ch in chapters if ch["id"] not in chapters_i_finished]

        t["chapters"] = chapters

    return sorted(titles, key=lambda t: len(t["chapters"]), reverse=True)


def read(user_id, site, title_id, chapter_id):
    run_sql(
        """
        INSERT INTO read (user_id, site, title_id, chapter_id) VALUES (?,?,?,?)
        ON CONFLICT (user_id, site, title_id, chapter_id)
        DO UPDATE SET updated_at=datetime('now');
        """,
        (user_id, site, title_id, chapter_id),
    )


def unread(user_id, site, title_id, chapter_id):
    run_sql(
        "DELETE FROM read WHERE user_id=? AND site=? AND title_id=? AND chapter_id=?;",
        (user_id, site, title_id, chapter_id),
    )


def find_outdated_titles(since="-6 hours"):
    return run_sql(
        "SELECT id, site FROM title WHERE updated_at <= datetime('now', ?);", (since,)
    )


class KeyvalStore:
    @staticmethod
    def get(key: str, default=None, since=None) -> str:
        if since is None:
            result = run_sql("SELECT value FROM keyval_store WHERE key=?;", (key,))
        else:
            result = run_sql(
                """
                SELECT value FROM keyval_store WHERE key=?
                AND updated_at >= datetime('now', ?);
                """,
                (key, since),
            )
        return result[0] if result else default

    @staticmethod
    def set(key: str, value: str):
        # let's not allow crap in by accident
        assert isinstance(key, str)
        assert isinstance(value, str)
        run_sql(
            """
            INSERT INTO keyval_store (key, value) VALUES (?,?)
            ON CONFLICT (key) DO UPDATE SET value=excluded.value, updated_at=datetime('now');
            """,
            (key, value),
        )


def import_follows(user_id: int, site_title_pairs: List[Tuple[str, str]]):
    run_sql_many(
        """
        INSERT INTO follow (user_id, site, title_id) VALUES (?, ?, ?)
        ON CONFLICT DO NOTHING;
        """,
        ((user_id, site, title_id) for site, title_id in site_title_pairs),
    )


def create_token(user_id, remember=False):
    lifespan = "+365 days" if remember else "+1 day"
    token = secrets.token_urlsafe(64)
    run_sql(
        """
        INSERT INTO token (user_id, token, lifespan) VALUES (?,?,?);
        """,
        (user_id, token, lifespan),
    )
    return token


def verify_token(token):
    """
    Checks if there's a matching token that hasn't exceeded its lifespan.
    If there's a match, refreshes its last_accessed_at value, effectively expanding
    its life.
    """
    result = run_sql(
        """
        SELECT user_id FROM token
        WHERE token=?
          AND datetime(last_accessed_at, lifespan) > datetime('now');
        """,
        (token,),
    )
    user_id = result[0] if len(result) == 1 else None
    if user_id:
        run_sql(
            "UPDATE token SET last_accessed_at = datetime('now') WHERE token=?;",
            (token,),
        )
    return user_id


def get_username(user_id):
    result = run_sql("SELECT username FROM user WHERE id=?;", (user_id,))
    assert len(result) == 1
    return result[0]


def delete_token(token):
    num_deleted = run_sql(
        "DELETE FROM token WHERE token=?;", (token,), return_num_affected=True
    )
    return num_deleted


def delete_expired_tokens():
    num_deleted = run_sql(
        """
        DELETE FROM token
        WHERE datetime(last_accessed_at, lifespan) < datetime('now');
        """,
        return_num_affected=True,
    )
    return num_deleted


def is_manga_page_url(url):
    """
    Checks if url exists in db as a page image.
    This is currently used to avoid abuse of our /proxy/ endpoint.
    """
    result = run_sql(
        """
        SELECT 1 FROM chapter, json_each(pages) WHERE value = ? LIMIT 1;
        """,
        (url,),
    )
    return len(result) == 1
