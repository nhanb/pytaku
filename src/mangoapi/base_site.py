import functools
from abc import ABC, abstractmethod

import cloudscraper
import requests

from .exceptions import (
    SourceSite5xxError,
    SourceSiteTimeoutError,
    SourceSiteUnexpectedError,
)


def create_session():
    return cloudscraper.create_scraper(
        {
            "mobile": False,
        }
    )


class Site(ABC):
    def __init__(self):
        self.username = None
        self.password = None
        self.is_logged_in = False
        self._session = create_session()

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

    def _http_request(self, method, url, *args, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = 5

        request_func = getattr(self._session, method)
        try:
            resp = request_func(url, *args, **kwargs)
        except requests.exceptions.Timeout:
            raise SourceSiteTimeoutError(url)

        if resp.status_code == 403:
            self._session = create_session()

        if 500 <= resp.status_code <= 599:
            raise SourceSite5xxError(url, resp.status_code, resp.text)
        elif resp.status_code != 200:
            raise SourceSiteUnexpectedError(url, resp.status_code, resp.text)

        return resp

    def http_get(self, *args, **kwargs):
        return self._http_request("get", *args, **kwargs)

    def http_post(self, *args, **kwargs):
        return self._http_request("post", *args, **kwargs)


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
