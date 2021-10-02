from abc import ABC, abstractmethod
from urllib.parse import urlparse

import requests

from pytaku.conf import config

from .exceptions import (
    SourceSite5xxError,
    SourceSiteTimeoutError,
    SourceSiteUnexpectedError,
)


def create_session():
    session = requests.Session()
    session.headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    return session


class Site(ABC):
    def __init__(self):
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
    def title_thumbnail(self, title_id, cover_ext):
        pass

    @abstractmethod
    def title_source_url(self, title_id):
        pass

    # optional abstract method
    def login(self, username, password):
        raise NotImplementedError()

    def _http_request(self, method, url, *args, **kwargs):
        headers = kwargs.get("headers", {})
        if "timeout" not in kwargs:
            kwargs["timeout"] = 5

        # Proxy shit
        parsed_url = urlparse(url)
        url = parsed_url._replace(
            netloc=config.OUTGOING_PROXY_NETLOC,
            scheme="https",
        ).geturl()
        headers["X-Proxy-Target-Host"] = parsed_url.netloc
        headers["X-Proxy-Key"] = config.OUTGOING_PROXY_KEY
        headers["X-Proxy-Scheme"] = parsed_url.scheme
        kwargs["headers"] = headers

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
