from secrets import token_urlsafe

from goodconf import GoodConf, Value


class Config(GoodConf):
    MANGADEX_USERNAME = Value()
    MANGADEX_PASSWORD = Value()

    FLASK_SECRET_KEY = Value(initial=lambda: token_urlsafe(50))


config = Config(default_files=["pytaku.conf.json"], load=True)
