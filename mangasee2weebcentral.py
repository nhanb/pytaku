import json

from mangoapi.weebcentral import Weebcentral
from pytaku.conf import config
from pytaku.database.common import run_sql
from pytaku.main import ensure_titles

config.load()
wc = Weebcentral()

with open("mangasee2weebcentral.json", "r") as file:
    mappings = json.load(file)

# First populate weebcentral titles in our db
site_title_pairs = [("weebcentral", title["wc_id"]) for title in mappings.values()]
ensure_titles(site_title_pairs)

# Now move follows from mangasee to weebcentral
follows = run_sql("select user_id, title_id from follow where site='mangasee'") or []
for follow in follows:
    user_id = follow["user_id"]
    old_title_id = follow["title_id"]
    new_title_id = mappings[old_title_id]["wc_id"]
    print(
        "Updating",
        old_title_id,
        "->",
        new_title_id,
        mappings[old_title_id]["wc_name"],
    )
    num_affected = run_sql(
        "update follow set title_id=?, site='weebcentral' where user_id=? and title_id=? and site='mangasee'",
        (new_title_id, user_id, old_title_id),
        return_num_affected=True,
    )
    assert num_affected == 1

# Lastly, migrate "read" markers by matching chapter.number

# Build lookup tables first: since we only have the title.chapters json array to work
# with, it's easier to build dumb lookup tables instead of wrestling with sqlite's json
# functions... I think.
ms_title_chapters = {}  # dict to look up chapter number of title id + chapter id
wc_title_chapters = {}  # dict to look up chapter id from title id + chapter number
for title in mappings.values():
    ms_title = run_sql(
        "select chapters from title where site='mangasee' and id=?",
        (title["ms_id"],),
    )
    ms_chapters = json.loads(ms_title[0])
    ms_title_chapters[title["ms_id"]] = {
        chapter["id"]: chapter["number"] for chapter in ms_chapters
    }

    wc_title = run_sql(
        "select chapters from title where site='weebcentral' and id=?",
        (title["wc_id"],),
    )
    wc_chapters = json.loads(wc_title[0])
    wc_title_chapters[title["wc_id"]] = {
        chapter["number"]: chapter["id"] for chapter in wc_chapters
    }


# Now update mangasee "read" records to point to weebcentral chapters that have matching
# chapter numbers:
reads = (
    run_sql("select user_id, title_id, chapter_id from \"read\" where site='mangasee'")
    or []
)
for read in reads:
    user_id = read["user_id"]
    old_title_id = read["title_id"]
    old_chapter_id = read["chapter_id"]

    new_title = mappings[old_title_id]
    new_title_id = new_title["wc_id"]

    # All of the previous dict building pays off here:
    chap_number = ms_title_chapters[old_title_id].get(old_chapter_id, None)
    if chap_number is None:
        print("Chap number not found:", user_id, old_title_id, old_chapter_id)
        continue

    new_chapter_id = wc_title_chapters[new_title_id].get(chap_number, None)
    if new_chapter_id is None:
        print("Found no matching new chapter:", user_id, old_title_id, old_chapter_id)
        continue

    print(
        ">>", user_id, old_title_id, old_chapter_id, "->", new_title_id, new_chapter_id
    )

    existing = run_sql(
        "select * from read where site='weebcentral' and user_id=? and title_id=? and chapter_id=?",
        (user_id, new_title_id, new_chapter_id),
    )
    if len(existing) > 0:
        print("Skipping duplicate:", user_id, old_title_id, old_chapter_id)
        continue

    num_affected = run_sql(
        'update "read"'
        " set site='weebcentral', title_id=?, chapter_id=?"
        " where site='mangasee' and user_id=? and title_id=? and chapter_id=?",
        (
            new_title_id,
            new_chapter_id,
            user_id,
            old_title_id,
            old_chapter_id,
        ),
        return_num_affected=True,
    )
    assert num_affected == 1
