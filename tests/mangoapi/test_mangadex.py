from mangoapi.mangadex import Mangadex
from pytaku.conf import config


def test_get_title():
    title = Mangadex().get_title("2597")
    assert title == {
        "id": "2597",
        "name": "Sayonara Football",
        "site": "mangadex",
        "cover_ext": "jpg",
        "alt_names": ["Adiós al fútbol", "さよならフットボール", "再见足球"],
        "is_webtoon": False,
        "descriptions": [
            "Nozomi wants to enter the newcomer's competition. But the coach is against it, because their club is a boy's football club and she's... a she. Will she be able to enter the match she wants to play in?"
        ],
        "chapters": [
            {
                "id": "84598",
                "name": "Epilogue",
                "volume": 2,
                "groups": ["Shoujo Crusade"],
                "number": "8",
                "num_major": 8,
            },
            {
                "id": "84596",
                "name": "Football Under the Blue Sky",
                "volume": 2,
                "groups": ["Shoujo Crusade"],
                "number": "7",
                "num_major": 7,
            },
            {
                "id": "84594",
                "name": "Everyone in a Crisis",
                "volume": 2,
                "groups": ["Shoujo Crusade"],
                "number": "6",
                "num_major": 6,
            },
            {
                "id": "84592",
                "name": "Clash and Decide",
                "volume": 2,
                "groups": ["Shoujo Crusade"],
                "number": "5",
                "num_major": 5,
            },
            {
                "id": "84590",
                "name": "And There's the Whistle",
                "volume": 1,
                "groups": ["Shoujo Crusade"],
                "number": "4",
                "num_major": 4,
            },
            {
                "id": "84589",
                "name": "A Plan to Become a Regular",
                "volume": 1,
                "groups": ["Shoujo Crusade"],
                "number": "3",
                "num_major": 3,
            },
            {
                "id": "84587",
                "name": "Her Determination at That Time",
                "volume": 1,
                "groups": ["Shoujo Crusade"],
                "number": "2",
                "num_major": 2,
            },
            {
                "id": "84585",
                "name": "The Entry of an Unmanageable Woman",
                "volume": 1,
                "groups": ["Shoujo Crusade"],
                "number": "1",
                "num_major": 1,
            },
        ],
    }


def test_get_title_webtoon():
    title = Mangadex().get_title("1")
    assert title["is_webtoon"] is True


def test_get_chapter():
    chap = Mangadex().get_chapter("doesn't matter", "696882")
    pages = chap.pop("pages")
    pages_alt = chap.pop("pages_alt")
    assert chap == {
        "id": "696882",
        "title_id": "12088",
        "site": "mangadex",
        "name": "Extras",
        "groups": ["Träumerei Scans", "GlassChair"],
        "number": "81.5",
        "num_major": 81,
        "num_minor": 5,
    }
    assert len(pages) == 16
    assert len(pages_alt) == 16


def test_search():
    md = Mangadex()
    md.username = config.MANGADEX_USERNAME
    md.password = config.MANGADEX_PASSWORD

    results = md.search_title("sayonara football")
    assert results == [
        {
            "id": "2597",
            "name": "Sayonara Football",
            "site": "mangadex",
            "thumbnail": "https://mangadex.org/images/manga/2597.large.jpg",
        }
    ]
