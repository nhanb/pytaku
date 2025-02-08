from mangoapi.weebcentral import Weebcentral


def test_get_title():
    title = Weebcentral().get_title("01J76XY7QH18K4Y6MS85GJKF3H")
    chapters = title.pop("chapters")
    assert title == {
        "id": "01J76XY7QH18K4Y6MS85GJKF3H",
        "name": "Yu Yu Hakusho",
        "site": "weebcentral",
        "cover_ext": "webp",
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
        "id": "01J76XYYF8TDH22V5BWENQA006",
        "name": "",
        "num_major": 63,
        "num_minor": 5,
        "number": "63.5",
        "volume": "",
    }


def test_get_chapter():
    chapter = Weebcentral().get_chapter(
        "01J76XY7QH18K4Y6MS85GJKF3H", "01J76XYYF8TDH22V5BWENQA006"
    )
    pages = chapter.pop("pages")
    pages_alt = chapter.pop("pages_alt")
    assert chapter == {
        "groups": [],
        "id": "01J76XYYF8TDH22V5BWENQA006",
        "name": "",
        "num_major": 63,
        "num_minor": 5,
        "number": "63.5",
        "site": "weebcentral",
        "title_id": "01J76XY7QH18K4Y6MS85GJKF3H",
    }
    assert pages[0].endswith("/manga/Yu-Yu-Hakusho/0063.5-001.png")
    assert pages[-1].endswith("/manga/Yu-Yu-Hakusho/0063.5-031.png")
    assert pages_alt == []


def test_search_title():
    site = Weebcentral()
    results = site.search_title("sayonara football")
    assert results[0] == {
        "id": "01J76XYAYWZXV9XB7SGZ2035YR",
        "name": "Sayonara, Football",
        "site": "weebcentral",
        "thumbnail": "https://temp.compsci88.com/cover/normal/01J76XYAYWZXV9XB7SGZ2035YR.webp",
    }
