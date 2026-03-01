import json
from dataclasses import dataclass


@dataclass
class Config:
    FLASK_SECRET_KEY: str
    MANGA_HOURS_UNTIL_OUTDATED = 6

    PROXY_PREFIX: str = ""
    # ^ use this to e.g. point to a CDN's domain
    PROXY_CACHE_DIR: str = "proxy_cache"
    PROXY_CACHE_MAX_SIZE: int = 1024 * 1024 * 1024 * 5  # 5GiB in bytes
    PROXY_CACHE_MAX_AGE: int = 3600 * 24 * 2  # 2 days in seconds

    OUTGOING_PROXY_NETLOC: str = ""
    OUTGOING_PROXY_KEY: str = ""


with open("pytaku.conf.json", "rb") as conf_file:
    config = Config(**json.load(conf_file))
