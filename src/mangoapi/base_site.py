import functools
from abc import ABC, abstractmethod


class Site(ABC):
    def __init__(self):
        self._cookies = None
        self.username = None
        self.password = None

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
        if self._cookies is None:
            assert self.username
            assert self.password
            self._cookies = self.login(self.username, self.password)
        return func(self, *args, **kwargs)

    return wrapper
