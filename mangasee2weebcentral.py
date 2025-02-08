import json

from mangoapi.weebcentral import Weebcentral
from pytaku.conf import config
from pytaku.main import ensure_titles

config.load()
wc = Weebcentral()

with open("mangasee2weebcentral.json", "r") as file:
    mappings = json.load(file)

site_title_pairs = [("weebcentral", title["wc_id"]) for title in mappings.values()]
ensure_titles(site_title_pairs)
