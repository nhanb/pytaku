from mangoapi.mangadex import Mangadex


def test_get_title():
    title = Mangadex().get_title("8af3ad21-3e7e-4fb5-b344-d0044ec154fc")
    chapters = title.pop("chapters")
    descriptions = title.pop("descriptions")
    assert descriptions[0]
    assert title == {
        "id": "8af3ad21-3e7e-4fb5-b344-d0044ec154fc",
        "name": "Beelzebub",
        "site": "mangadex",
        "cover_ext": "bab3ccbf-7479-4117-ad92-4dedced54ceb.jpg",
        "alt_names": [
            "Beruzebabu",
            "Вельзевул",
            "เด็กพันธุ์นรกสั่งลุย",
            "べるぜバブ",
            "恶魔奶爸",
            "惡魔奶爸",
            "바알세불",
            "बेलजेबब",
        ],
        "descriptions_format": "html",
        "is_webtoon": False,
    }

    assert len(chapters) == 251
    assert chapters[1] == {
        "id": "dfd3fd5a-a20f-460f-b726-e9cb168bfe3d",
        "name": "Love Blooms in The Season of Partings",
        "volume": "28",
        "groups": [],
        "number": "245",
        "num_major": 245,
    }
    assert chapters[-1] == {
        "groups": [],
        "id": "91ee8504-db4e-4b67-ac89-8fb291f67f7e",
        "name": "I Picked up the Devil King",
        "num_major": 1,
        "number": "1",
        "volume": "1",
    }


def test_get_title_webtoon():
    title = Mangadex().get_title("6e3553b9-ddb5-4d37-b7a3-99998044774e")
    assert title["is_webtoon"] is True


def test_get_chapter():
    chap = Mangadex().get_chapter("_", "7f49d795-d525-4b65-9fd8-ddb58425683e")
    pages = chap.pop("pages")
    pages_alt = chap.pop("pages_alt")
    assert chap == {
        "id": "7f49d795-d525-4b65-9fd8-ddb58425683e",
        "title_id": "6e3553b9-ddb5-4d37-b7a3-99998044774e",
        "site": "mangadex",
        "name": "Volume 15 Extras (Epilogue & Prologue)",
        "groups": [],
        "number": "222.5",
        "num_major": 222,
        "num_minor": 5,
    }
    assert len(pages) == 53
    assert len(pages_alt) == 0


def test_search():
    md = Mangadex()
    results = md.search_title("beelzebub")
    assert sorted(results, key=lambda x: x["name"]) == sorted(
        [
            {
                "id": "8af3ad21-3e7e-4fb5-b344-d0044ec154fc",
                "name": "Beelzebub",
                "site": "mangadex",
                "thumbnail": "https://uploads.mangadex.org/covers/8af3ad21-3e7e-4fb5-b344-d0044ec154fc/bab3ccbf-7479-4117-ad92-4dedced54ceb.jpg.256.jpg",
            },
            {
                "id": "72378871-9afc-47bd-902f-0d8116adb390",
                "name": "Beelzebub - Digital Colored Comics",
                "site": "mangadex",
                "thumbnail": "https://uploads.mangadex.org/covers/72378871-9afc-47bd-902f-0d8116adb390/c8b9b385-b7b9-4101-bf71-4f0d66fc35ff.jpg.256.jpg",
            },
            {
                "id": "b4320039-9b91-44a7-a60d-c7ba8c0684e7",
                "name": "Beelzebub-jou no Oki ni Mesu mama.",
                "site": "mangadex",
                "thumbnail": "https://uploads.mangadex.org/covers/b4320039-9b91-44a7-a60d-c7ba8c0684e7/dc879d3e-5cfd-4651-ab79-6fa6b37d9664.jpg.256.jpg",
            },
            {
                "id": "a453af66-0dac-4966-b246-b37c96b27245",
                "name": "Makai kara Kita Maid-san",
                "site": "mangadex",
                "thumbnail": "https://uploads.mangadex.org/covers/a453af66-0dac-4966-b246-b37c96b27245/7e50b22d-b027-4ee1-bd15-94f05fa6cecb.jpg.256.jpg",
            },
        ],
        key=lambda x: x["name"],
    )


def test_get_title_with_empty_descriptions():
    title = Mangadex().get_title("fc102424-d94b-4a1b-98bc-d5062cd768d6")
    assert title["descriptions"] == []
