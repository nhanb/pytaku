import functools
from abc import ABC, abstractmethod

import requests


class Site(ABC):
    def __init__(self):
        self.username = None
        self.password = None
        self.is_logged_in = False
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
            }
        )

    @abstractmethod
    def get_title(self, title_id):
        pass

    @abstractmethod
    def get_chapter(self, title_id, chapter_id):
        pass

    @abstractmethod
    def search_title(self, query):
        pass

    @abstractmethod
    def title_cover(self, title_id, cover_ext):
        pass

    @abstractmethod
    def title_thumbnail(self, title_id):
        pass

    @abstractmethod
    def title_source_url(self, title_id):
        pass

    # optional abstract method
    def login(self, username, password):
        raise NotImplementedError()


def requires_login(func):
    """
    Decorator designed for use on a Site's instance methods.
    It ensures cookies are ready before running the method.
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # TODO: replace is_logged_in flag check with actual "if rejected then try
        # logging in" logic, just in case login cookies expire.
        if not self.is_logged_in:
            assert self.username
            assert self.password
            self.login(self.username, self.password)
        return func(self, *args, **kwargs)

    return wrapper
