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
        "name": "Chapter 63.5",
        "num_major": 63,
        "num_minor": 5,
        "number": "63.5",
        "volume": "",
    }


def test_get_title_custom_chapter_name():
    title = Weebcentral().get_title("01J76XY7HA6DH9YYGREDVPH8W5")
    chapters = title.pop("chapters")
    assert title == {
        "id": "01J76XY7HA6DH9YYGREDVPH8W5",
        "name": "Case Closed",
        "site": "weebcentral",
        "cover_ext": "webp",
        "alt_names": [],
        "descriptions": [
            "Shinichi Kudo is a high-school student who, by using "
            "observation and deduction, is good at solving mysteries. "
            "While investigating one, he is caught by the criminals that "
            "he was watching and forced to take an experimental drug. "
            "Leaving him for dead, the criminals disappear. Instead of "
            "killing him, however, the drug turns Shinichi into a little "
            "kid. ",
            "To preserve the illusion of his 'disappearance,' Shinichi "
            "adopts a new name based on his favorite author (Arthur "
            "Conan Doyle) and becomes Conan Edogawa. Ran, his (actually "
            "Shinichi's) childhood friend takes this little boy under "
            "her wing and brings him to her home. Conan now lives at a "
            "detective agency run by Ran's father, but his mind is as "
            "keen as ever and he continues to solve mysteries... always "
            "allowing Ran's father to take all the credit. ",
            "As far as everyone's concerned, Conan is just a little kid "
            "anyway... even to Ran. This is *extremely* frustrating to "
            "Conan since nobody will listen to a 'little boy.' Despite "
            "this, Conan has a mission... to find the criminals who did "
            "this to him and get the antidote to that drug.",
        ],
        "descriptions_format": "text",
        "is_webtoon": False,
    }
    assert len(chapters) >= 1139
    assert chapters[-1]["name"] == "File 1"


def test_get_title_3k_chapters():
    title = Weebcentral().get_title("01J76XYCMB1GPHFV1SCDE4KHB2")
    chapters = title.pop("chapters")
    assert title == {
        "id": "01J76XYCMB1GPHFV1SCDE4KHB2",
        "name": "Martial Peak",
        "site": "weebcentral",
        "cover_ext": "webp",
        "alt_names": [],
        "descriptions": [
            "The journey to the martial peak is a lonely, solitary and "
            "long one.In the face of adversity,you must survive and "
            "remain unyielding.Only then can you break through and and "
            "continue on your journey to become the strongest. Sky Tower "
            "tests its disciples in the harshest ways to prepare them "
            "for this journey.One day the lowly sweeper Yang Kai managed "
            "to obtain a black book, setting him on the road to the peak "
            "of the martials world.",
            "NOTE: OFFICIAL and FAN versions have different numbering "
            "systems. There is nothing missing or extra.",
        ],
        "descriptions_format": "text",
        "is_webtoon": False,
    }
    assert len(chapters) >= 3553
    assert chapters[-1] == {
        "groups": [],
        "id": "01J76XZ2DAADMHYVAMPATCM5Q6",
        "name": "Chapter 1",
        "num_major": 1,
        "num_minor": 0,
        "number": "1",
        "volume": "",
    }


def test_get_title_unescape_html():
    title = Weebcentral().get_title("01J76XYC37HDCA5SD6QP3D0GN7")
    assert title["name"] == "If You're Gonna Dress up, Do It Like This"


def test_get_chapter():
    chapter = Weebcentral().get_chapter(
        "01J76XY7QH18K4Y6MS85GJKF3H", "01J76XYYF8TDH22V5BWENQA006"
    )
    pages = chapter.pop("pages")
    pages_alt = chapter.pop("pages_alt")
    assert chapter == {
        "groups": [],
        "id": "01J76XYYF8TDH22V5BWENQA006",
        "name": "Chapter 63.5",
        "num_major": 63,
        "num_minor": 5,
        "number": "63.5",
        "site": "weebcentral",
        "title_id": "01J76XY7QH18K4Y6MS85GJKF3H",
    }
    assert pages[0].endswith("/manga/Yu-Yu-Hakusho/0063.5-001.png")
    assert pages[-1].endswith("/manga/Yu-Yu-Hakusho/0063.5-031.png")
    assert pages_alt == []


def test_get_chapter_custom_name():
    chapter = Weebcentral().get_chapter(
        "01J76XY7HA6DH9YYGREDVPH8W5", "01J76XYYH1X0HS61FJG7FA3Q34"
    )
    assert chapter["name"] == "File 1"


def test_search_title():
    site = Weebcentral()
    results = site.search_title("if you're gonna dress up, do it like this")
    assert results[0] == {
        "id": "01J76XYC37HDCA5SD6QP3D0GN7",
        "name": "If You're Gonna Dress up, Do It Like This",
        "site": "weebcentral",
        "thumbnail": "https://temp.compsci88.com/cover/normal/01J76XYC37HDCA5SD6QP3D0GN7.webp",
    }
