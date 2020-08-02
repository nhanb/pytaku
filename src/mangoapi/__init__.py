import re

import requests

# Titles regex slightly adapted from https://github.com/md-y/mangadex-full-api
# Thanks!
TITLES_PATTERN = re.compile(
    r"""<a[^>]*href=["']\/title\/(\d+)\/\S+["'][^>]*manga_title[^>]*>([^<]*)<"""
)


def _parse_chapter_number(string):
    nums = string.split(".")
    count = len(nums)
    assert count == 1 or count == 2
    result = {"number": string}
    result["num_major"] = int(nums[0])
    if count == 2:
        result["num_minor"] = int(nums[1])
    return result


def _extract_groups(chap):
    return [
        group.strip()
        for group in [chap["group_name"], chap["group_name_2"], chap["group_name_3"]]
        if group
    ]


def get_title(title_id):
    url = f"https://mangadex.org/api/?id={title_id}&type=manga"
    md_resp = requests.get(url)
    assert md_resp.status_code == 200, md_resp.text
    md_json = md_resp.json()
    assert md_json["status"] == "OK"

    cover = md_json["manga"]["cover_url"].split("/")[-1]
    cover_ext = cover[cover.find(".") + 1 : cover.rfind("?")]

    title = {
        "id": title_id,
        "name": md_json["manga"]["title"],
        "cover_ext": cover_ext,
        "alt_names": md_json["manga"]["alt_names"],
        "descriptions": md_json["manga"]["description"].split("\r\n\r\n"),
        "chapters": [
            {
                "id": chap_id,
                "name": chap["title"],
                "volume": int(chap["volume"]) if chap["volume"] else None,
                "groups": _extract_groups(chap),
                **_parse_chapter_number(chap["chapter"]),
            }
            for chap_id, chap in md_json["chapter"].items()
            if chap["lang_code"] == "gb" and chap["group_name"] != "MangaPlus"
        ],
    }
    return title


def get_chapter(chapter_id):
    md_resp = requests.get(
        f"https://mangadex.org/api/?id={chapter_id}&type=chapter&saver=0"
    )
    assert md_resp.status_code == 200, md_resp.text
    md_json = md_resp.json()
    assert md_json["status"] == "OK"

    server = md_json.get("server_fallback") or md_json["server"]
    img_path = f"{server}{md_json['hash']}"

    chapter = {
        "id": chapter_id,
        "title_id": md_json["manga_id"],
        "name": md_json["title"],
        "pages": [f"{img_path}/{page}" for page in md_json["page_array"]],
        "groups": _extract_groups(md_json),
        "is_webtoon": md_json["long_strip"] == 1,
        **_parse_chapter_number(md_json["chapter"]),
    }
    return chapter


def login(username, password):
    """
    Returns cookies of a logged in user.
    """
    form_data = {
        "login_username": username,
        "login_password": password,
        "two_factor": "",
        "remember_me": "1",
    }
    md_resp = requests.post(
        "https://mangadex.org/ajax/actions.ajax.php?function=login",
        data=form_data,
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    assert md_resp.status_code == 200, md_resp.text
    return dict(md_resp.cookies)


def search_title(user_cookies, query):
    md_resp = requests.get(
        f"https://mangadex.org/quick_search/{query}", cookies=user_cookies,
    )
    assert md_resp.status_code == 200, md_resp.text

    matches = TITLES_PATTERN.findall(md_resp.text)
    titles = [{"id": int(id), "name": name.strip()} for id, name in matches]
    return titles
