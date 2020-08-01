from mangoapi import login
from pytaku.conf import config

assert config.MANGADEX_USERNAME
assert config.MANGADEX_PASSWORD

_cookies = None


def get_cookies():
    global _cookies
    if _cookies is None:
        print("Logging in to mangadex")
        _cookies = login(config.MANGADEX_USERNAME, config.MANGADEX_PASSWORD)
    else:
        print("Reusing mangadex cookies")
    return _cookies
