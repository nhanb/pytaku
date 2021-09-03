import csv
import html
import os.path
import re
import time
from pprint import pprint

import requests

from pytaku.database.common import get_conn, run_sql

CSV_FILE_NAME = "names.csv"


def populate_csv():
    """
    Running this as main script entry will:
    - Query all existing mangadex titles in db (around 370 at the moment)
    - For each title, throw its name into MD's new search API
        + iterate through possible results, normalize them (replace all non-alphanumeric
          chars with single space), compare for exact match on normalized form, grab the
          new uuid.
        + save (id, name, new_id) in csv

    This script is resumable.
    """
    titles = find_mangadex_titles()
    dones = done_ids()
    pending_titles = [t for t in titles if t["id"] not in dones]
    lazy_rows = rows_generator(pending_titles)
    write_csv(lazy_rows)


def migrate_title_ids():
    """
    After running populate_csv(), open up the csv, fill any blanks, then run this: it
    will update title IDs in all affected tables
    """
    with open(CSV_FILE_NAME, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        cur = get_conn().cursor()
        cur.execute("PRAGMA foreign_keys = off;")
        cur.execute("BEGIN TRANSACTION;")
        for row in reader:
            old = row["id"]
            new = row["new_id"]
            print(f"{old} => {new}")
            cur.execute("UPDATE title SET id=? WHERE id=?;", (new, old))
            cur.execute(
                "UPDATE chapter SET title_id=? WHERE title_id=? and site='mangadex';",
                (new, old),
            )
            cur.execute(
                "UPDATE read SET title_id=? WHERE title_id=? and site='mangadex';",
                (new, old),
            )
            cur.execute(
                "UPDATE follow SET title_id=? WHERE title_id=? and site='mangadex';",
                (new, old),
            )
        cur.execute("PRAGMA foreign_key_check;")
        cur.execute("COMMIT;")
        cur.execute("PRAGMA foreign_keys = on;")


def rows_generator(titles):
    for title in titles:
        old_id = title["id"]
        name = title["name"]
        new_id = look_for_match(name) or ""

        yield {
            "id": old_id,
            "name": name,
            "new_id": new_id,
        }


def write_csv(rows):
    is_resuming = os.path.isfile(CSV_FILE_NAME)
    print("Is resuming:", is_resuming)

    with open(CSV_FILE_NAME, "a", newline="") as csvfile:
        fieldnames = ["id", "name", "new_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not is_resuming:
            writer.writeheader()

        for row in rows:
            print()
            pprint(row)
            print()
            writer.writerow(row)


def done_ids():
    with open(CSV_FILE_NAME, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        return {row["id"] for row in reader}


def look_for_match(old_title):
    offset = 0
    limit = 100
    total = 999_999
    normalized_old_title = normalize(old_title)

    while True:
        print(f"-- Searching {old_title}, offset={offset}")
        resp = requests.get(
            "https://api.mangadex.org/manga",
            params={
                "limit": limit,
                "offset": offset,
                "title": old_title,
                "order[title]": "asc",
            },
        )

        if resp.status_code == 400 and resp.json()["errors"][0]["detail"].startswith(
            "Result window is too large"
        ):
            return None

        assert resp.status_code == 200, (resp.status_code, resp.content)

        resp_json = resp.json()
        total = resp_json["total"]

        for result in resp_json["results"]:
            titles = result["data"]["attributes"]["title"]
            title = titles.get("en") or titles.get("jp") or titles.get("ja", "")
            if not title:
                print(">> Weird title lang:", titles)
            normalized_title = normalize(title)
            if normalized_old_title == normalized_title:
                return result["data"]["id"]

        offset += limit
        if offset >= total:
            break
        else:
            time.sleep(0.25)

    return None


def normalize(title: str):
    title = title.lower()
    title = re.sub("[^0-9a-zA-Z]+", " ", title)
    return title.strip()


def find_mangadex_titles():
    """
    Returns list of dict: {"id", "name"}
    """
    results = run_sql("SELECT id, name FROM title WHERE site='mangadex' order by name;")
    for result in results:
        result["name"] = html.unescape(result["name"])

    return results


if __name__ == "__main__":
    migrate_title_ids()
