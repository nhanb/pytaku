from secrets import token_urlsafe

from goodconf import GoodConf, Value


class Config(GoodConf):
    FLASK_SECRET_KEY = Value(initial=lambda: token_urlsafe(50))

    MANGA_HOURS_UNTIL_OUTDATED = Value(default=6)

    PROXY_PREFIX = Value(default="")
    # ^ use this to e.g. point to a CDN's domain
    PROXY_CACHE_DIR = Value(default="proxy_cache")
    PROXY_CACHE_MAX_SIZE = Value(default=1024 * 1024 * 1024 * 5)  # 5GiB in bytes
    PROXY_CACHE_MAX_AGE = Value(default=3600 * 24 * 2)  # 2 days in seconds

    OUTGOING_PROXY_NETLOC = Value()
    OUTGOING_PROXY_KEY = Value()


config = Config(default_files=["pytaku.conf.json"])
