from mangoapi.weebdex import Weebdex


def test_get_title():
    title = Weebdex().get_title("op7viak0in")
    chapters = title.pop("chapters")
    assert title == {
        "alt_names": [],
        "cover_ext": "rwxhcbx8y9",
        "descriptions": [
            "Before Naruto's birth, a great demon fox had attacked the Hidden Leaf "
            "Village. The 4th Hokage from the leaf village sealed the demon inside "
            "the newly born Naruto, causing him to unknowingly grow up detested by "
            "his fellow villagers. Despite his lack of talent in many areas of "
            "ninjutsu, Naruto strives for only one goal: to gain the title of "
            "Hokage, the strongest ninja in his village. Desiring the respect he "
            "never received, Naruto works toward his dream with fellow friends "
            "Sasuke and Sakura and mentor Kakashi as they go through many trials "
            "and battles that come with being a ninja.  ",
            "\n---",
        ],
        "descriptions_format": "text",
        "id": "op7viak0in",
        "is_webtoon": False,
        "name": "Naruto",
        "site": "weebdex",
    }
    assert len(chapters) == 703
    assert chapters[0] == {
        "groups": [],
        "id": "e9nun486ia",
        "name": "Uzumaki Naruto!!",
        "num_major": "700",
        "number": "700",
        "volume": "72",
    }


def test_get_chapter():
    chapter = Weebdex().get_chapter("e8y6hpg92d", "moysw1zb7p")
    pages = chapter.pop("pages")
    pages_alt = chapter.pop("pages_alt")
    assert chapter == {
        "groups": [],
        "id": "moysw1zb7p",
        "name": "Thank You for Reading",
        "num_major": "175",
        "num_minor": "5",
        "number": "175.5",
        "site": "weebdex",
        "title_id": "e8y6hpg92d",
    }
    assert pages[0].endswith(
        "1-d3616ca72d0c4cf3df37ddea486ef9b97115685312685fd243ec732df563c327.jpg"
    )
    assert pages[-1].endswith(
        "5-02b1c06d356d361dd94543ea40d0afdf70ae46b483f0e920e3e5577de62abe36.jpg"
    )
    assert pages_alt == []


def test_search_title():
    site = Weebdex()
    results = site.search_title("if you're gonna dress up, do it like this")
    assert results[0] == {
        "id": "tjub38rmhn",
        "name": "Fuku o Kiru nara Konna Fuu ni",
        "site": "weebdex",
        "thumbnail": "https://weebdex.org/covers/tjub38rmhn/hf7n8evvsw.256.webp",
    }
