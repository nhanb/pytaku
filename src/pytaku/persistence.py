import json

import apsw
import argon2

from .database.common import get_conn


def save_title(title):
    conn = get_conn()
    conn.cursor().execute(
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
            "site": "mangadex",
            "cover_ext": title["cover_ext"],
            "chapters": json.dumps(title["chapters"]),
            "alt_names": json.dumps(title["alt_names"]),
            "descriptions": json.dumps(title["descriptions"]),
        },
    )


def load_title(title_id):
    conn = get_conn()
    result = list(
        conn.cursor().execute(
            """
    SELECT id, name, site, cover_ext, chapters, alt_names, descriptions
    FROM title
    WHERE id = ?
      AND datetime(updated_at) > datetime('now', '-6 hours');
    """,
            (title_id,),
        )
    )
    if not result:
        return None
    elif len(result) > 1:
        raise Exception(f"Found multiple results for title_id {title_id}!")
    else:
        title = result[0]
        return {
            "id": title[0],
            "name": title[1],
            "site": title[2],
            "cover_ext": title[3],
            "chapters": json.loads(title[4]),
            "alt_names": json.loads(title[5]),
            "descriptions": json.loads(title[6]),
        }


def save_chapter(chapter):
    conn = get_conn()
    conn.cursor().execute(
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
            "site": "mangadex",
            "num_major": chapter["num_major"],
            "num_minor": chapter.get("num_minor", None),
            "name": chapter["name"],
            "pages": json.dumps(chapter["pages"]),
            "groups": json.dumps(chapter["groups"]),
            "is_webtoon": chapter["is_webtoon"],
        },
    )


def load_chapter(chapter_id):
    conn = get_conn()
    result = list(
        conn.cursor().execute(
            """
    SELECT id, title_id, num_major, num_minor, name, pages, groups, is_webtoon
    FROM chapter
    WHERE id = ?;
    """,
            (chapter_id,),
        )
    )
    if not result:
        return None
    elif len(result) > 1:
        raise Exception(f"Found multiple results for chapter_id {chapter_id}!")
    else:
        chapter = result[0]
        return {
            "id": chapter[0],
            "title_id": chapter[1],
            "num_major": chapter[2],
            "num_minor": chapter[3],
            "name": chapter[4],
            "pages": json.loads(chapter[5]),
            "groups": json.loads(chapter[6]),
            "is_webtoon": chapter[7],
        }


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
        get_conn().cursor().execute(
            "INSERT INTO user (username, password) VALUES (?, ?);",
            (username, hashed_password),
        )
        return None
    except apsw.ConstraintError as e:
        if "UNIQUE" in str(e):
            return "Username already exists."
        raise


def verify_username_password(username, password):
    data = list(
        get_conn()
        .cursor()
        .execute("SELECT password FROM user WHERE username = ?;", (username,))
    )
    if len(data) != 1:
        print(f"User {username} doesn't exist.")
        return False

    hasher = argon2.PasswordHasher()
    hash = data[0][0]
    try:
        hasher.verify(hash, password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        print(f"User {username} exists but password doesn't match.")
        return False
