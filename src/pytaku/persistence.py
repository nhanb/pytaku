import json

import argon2

import apsw

from .database.common import run_sql, run_sql_on_demand


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
                  INNER JOIN chapter c ON c.id = r.chapter_id AND c.site = r.site
                WHERE r.user_id = ?
                  AND c.title_id = ?
                  AND c.site = ?
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
        :groups,
        :is_webtoon
    );
    """,
        {
            "id": chapter["id"],
            "title_id": chapter["title_id"],
            "site": chapter["site"],
            "num_major": chapter.get("num_major"),
            "num_minor": chapter.get("num_minor"),
            "name": chapter["name"],
            "pages": json.dumps(chapter["pages"]),
            "groups": json.dumps(chapter["groups"]),
            "is_webtoon": chapter["is_webtoon"],
        },
    )


def load_chapter(site, title_id, chapter_id):
    result = run_sql(
        """
        SELECT id, title_id, site, num_major, num_minor, name, pages, groups, is_webtoon
        FROM chapter
        WHERE site=? AND title_id=? AND id=?;
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
        "INSERT INTO follow (user_id, site, title_id) VALUES (?, ?, ?);",
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
        chapters_i_finished = run_sql_on_demand(
            """
            SELECT r.chapter_id
            FROM read r
                INNER JOIN chapter c ON c.id = r.chapter_id AND c.site = r.site
            WHERE r.user_id = ?
                AND c.title_id = ?
                AND c.site = ?
            ORDER BY c.num_major desc, c.num_minor desc;
            """,
            (user_id, t["id"], t["site"]),
        )
        # Cut off chapter list:
        # only show chapters newer than the latest chapter that user has finished.
        # Running a loop here instead of just picking the one latest finished chapter
        # because source site may have deleted said chapter.
        for finished_chapter_id in chapters_i_finished:
            for i, ch in enumerate(chapters):
                if finished_chapter_id == ch["id"]:
                    chapters = chapters[:i]
                    break

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
