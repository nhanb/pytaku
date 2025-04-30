from secrets import token_urlsafe

from goodconf import Field, GoodConf


class Config(GoodConf):
    model_config = {"default_files": ["pytaku.conf.json"]}

    FLASK_SECRET_KEY: str = Field(initial=lambda: token_urlsafe(50))

    MANGA_HOURS_UNTIL_OUTDATED: int = Field(default=6)

    PROXY_PREFIX: str = Field(default="")
    # ^ use this to e.g. point to a CDN's domain
    PROXY_CACHE_DIR: str = Field(default="proxy_cache")
    PROXY_CACHE_MAX_SIZE: int = Field(default=1024 * 1024 * 1024 * 5)  # 5GiB in bytes
    PROXY_CACHE_MAX_AGE: int = Field(default=3600 * 24 * 2)  # 2 days in seconds

    OUTGOING_PROXY_NETLOC: str = Field()
    OUTGOING_PROXY_KEY: str = Field()


config = Config()
