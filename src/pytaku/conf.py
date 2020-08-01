from goodconf import GoodConf, Value


class Config(GoodConf):
    MANGADEX_USERNAME = Value()
    MANGADEX_PASSWORD = Value()


config = Config(default_files=["pytaku.conf.json"], load=True)
