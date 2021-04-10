import subprocess

from mangoapi.mangasee import Mangasee
from pytaku.database.common import get_conn, run_sql
from pytaku.persistence import save_title

ms = Mangasee()


def fetch_title(title_id: str):
    title = ms.get_title(title_id)
    updates = [(title_id, ch["number"], ch["id"]) for ch in title["chapters"]]
    return title, updates


def migrate():
    mangasee_titles = run_sql(
        "SELECT id FROM title WHERE site = 'mangasee' ORDER BY lower(id);"
    )
    print(f"There are {len(mangasee_titles)} titles to update.")

    diffs = []
    new_titles = []
    for title_id in mangasee_titles:
        print(f">> Fetching {title_id}")
        new_title, new_title_diffs = fetch_title(title_id)
        diffs += new_title_diffs
        new_titles.append(new_title)

    print("Diffs:")
    for diff in diffs:
        print(diff)

    print("Starting db transaction")
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("pragma foreign_keys = off;")
    cursor.execute("begin transaction;")

    for new_title in new_titles:
        print(f'Saving title {new_title["id"]}')
        save_title(new_title)

    for title_id, old_chapter_id, new_chapter_id in diffs:
        print("Updating", title_id, old_chapter_id, "to", new_chapter_id)
        cursor.execute(
            "UPDATE chapter SET id=? WHERE id=? AND title_id=? AND site='mangasee';",
            (new_chapter_id, old_chapter_id, title_id),
        )
        cursor.execute(
            "UPDATE read SET chapter_id=? WHERE chapter_id=? AND title_id=? AND site='mangasee';",
            (new_chapter_id, old_chapter_id, title_id),
        )

    cursor.execute("pragma foreign_key_check;")
    cursor.execute("commit;")
    cursor.execute("pragma foreign_keys = on;")
    print("All done!")


def main():
    subprocess.run(["systemctl", "--user", "stop", "pytaku"], check=True)
    subprocess.run(["systemctl", "--user", "stop", "pytaku-scheduler"], check=True)

    migrate()

    subprocess.run(["systemctl", "--user", "start", "pytaku"], check=True)
    subprocess.run(["systemctl", "--user", "start", "pytaku-scheduler"], check=True)


if __name__ == "__main__":
    main()
