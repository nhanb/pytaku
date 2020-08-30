from secrets import token_urlsafe

from goodconf import GoodConf, Value


class Config(GoodConf):
    MANGADEX_USERNAME = Value()
    MANGADEX_PASSWORD = Value()
    FLASK_SECRET_KEY = Value(initial=lambda: token_urlsafe(50))

    PROXY_PREFIX = Value(default="")
    # ^ use this to e.g. point to a CDN's domain
    PROXY_CACHE_DIR = Value(default="proxy_cache")
    PROXY_CACHE_MAX_SIZE = Value(default=1024 * 1024 * 1024 * 5)  # 5GiB in bytes
    PROXY_CACHE_MAX_AGE = Value(default=3600 * 24 * 2)  # 2 days in seconds


config = Config(default_files=["pytaku.conf.json"])
