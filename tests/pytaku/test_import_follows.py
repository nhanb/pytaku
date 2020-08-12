from pytaku.main import read_tachiyomi_follows


def test_read_tachiyomi_follows():
    data = """
{
  "version": 2,
  "mangas": [
    { "manga": ["/manga/Ajin", "Ajin", 9, 0, 0] },
    {
      "manga": [
        "/manga/28664/",
        "Ano Hito no I ni wa Boku ga Tarinai",
        2499283573021220255,
        0,
        0
      ]
    },
    { "manga": ["/manga/Chainsaw-Man", "Chainsaw Man", 9, 0, 0] },
    { "manga": ["/manga/Chi-No-Wadachi", "Chi no Wadachi", 9, 0, 0] },
    { "manga": ["/manga/13318/", "Dagashi Kashi", 2499283573021220255, 0, 0] },
    { "manga": ["/manga/31688/", "Dai Dark", 2499283573021220255, 0, 0] }
  ],
  "categories": [],
  "extensions": [
    "1998944621602463790:MANGA Plus by SHUEISHA",
    "2499283573021220255:MangaDex",
    "4637971935551651734:Guya",
    "9064882169246918586:Jaimini's Box",
    "9:Mangasee"
  ]
}
    """
    assert read_tachiyomi_follows(data) == [
        ("mangasee", "Ajin"),
        ("mangadex", "28664"),
        ("mangasee", "Chainsaw-Man"),
        ("mangasee", "Chi-No-Wadachi"),
        ("mangadex", "13318"),
        ("mangadex", "31688"),
    ]
