from mangoapi.mangasee import Mangasee


def test_get_title():
    title = Mangasee().get_title("Yu-Yu-Hakusho")
    chapters = title.pop("chapters")
    assert title == {
        "id": "Yu-Yu-Hakusho",
        "name": "Yu Yu Hakusho",
        "site": "mangasee",
        "cover_ext": "jpg",
        "alt_names": [],
        "descriptions": [
            "Yusuke Urameshi was a tough teen delinquent until one selfless act changed his life... by ending it. When he died saving a little kid from a speeding car, the afterlife didn't know what to do with him, so it gave him a second chance at life. Now, Yusuke is a ghost with a mission, performing good deeds at the behest of Botan, the ferrywoman of the River Styx, and Koenma, the pacifier-sucking judge of the dead."
        ],
        "descriptions_format": "text",
        "is_webtoon": False,
    }
    assert len(chapters) == 176
    assert chapters[112] == {
        "groups": [],
        "id": "100635",
        "raw_id": "100635",
        "name": "",
        "num_major": 63,
        "num_minor": 5,
        "number": "63.5",
        "volume": "",
    }


def test_get_chapter():
    chapter = Mangasee().get_chapter("Yu-Yu-Hakusho", "100635")
    pages = chapter.pop("pages")
    pages_alt = chapter.pop("pages_alt")
    assert chapter == {
        "groups": [],
        "id": "100635",
        "raw_id": "100635",
        "name": "",
        "num_major": 63,
        "num_minor": 5,
        "number": "63.5",
        "site": "mangasee",
        "title_id": "Yu-Yu-Hakusho",
    }
    assert pages[0].endswith("/manga/Yu-Yu-Hakusho/0063.5-001.png")
    assert pages[-1].endswith("/manga/Yu-Yu-Hakusho/0063.5-031.png")
    assert pages_alt == []


def test_search_title():
    class DictKeyvalStore(dict):
        def get(self, key):
            return self[key]

        def set(self, key, val):
            self[key] = val

    ms = Mangasee()
    ms.keyval_store = DictKeyvalStore()
    results = ms.search_title("sayonara football")
    assert results == [
        {
            "id": "Sayonara-Football",
            "name": "Sayonara, Football",
            "site": "mangasee",
            "thumbnail": "https://cover.nep.li/cover/Sayonara-Football.jpg",
        }
    ]
