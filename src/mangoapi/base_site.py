from abc import ABC, abstractmethod
from urllib.parse import urlparse

import requests

from pytaku.conf import config

from .exceptions import (
    SourceSite5xxError,
    SourceSite404Error,
    SourceSiteTimeoutError,
    SourceSiteUnexpectedError,
)

CHROME_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"


def create_session(user_agent: str | None):
    session = requests.Session()
    if user_agent is not None:
        session.headers["User-Agent"] = user_agent
    return session


class Site(ABC):
    # A subclass can set this to None to disable UA faking at all (see: Mangadex)
    user_agent: str | None = CHROME_USER_AGENT

    def __init__(self):
        self._session = create_session(self.user_agent)

    @abstractmethod
    def get_title(self, title_id) -> dict:
        pass

    @abstractmethod
    def get_chapter(self, title_id, chapter_id) -> dict:
        pass

    @abstractmethod
    def search_title(self, query) -> list[dict]:
        pass

    @abstractmethod
    def title_cover(self, title_id, cover_ext) -> str:
        pass

    @abstractmethod
    def title_thumbnail(self, title_id, cover_ext) -> str:
        pass

    @abstractmethod
    def title_source_url(self, title_id) -> str:
        pass

    # optional abstract method
    def login(self, username, password):
        raise NotImplementedError()

    def _http_request(self, method, url, *args, **kwargs):
        headers = kwargs.get("headers", {})
        if "timeout" not in kwargs:
            kwargs["timeout"] = 15

        # print(">>", url, args, kwargs)

        # Proxy shit
        if config.OUTGOING_PROXY_NETLOC:
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
            self._session = create_session(self.user_agent)

        if 500 <= resp.status_code <= 599:
            raise SourceSite5xxError(url, resp.status_code, resp.text)
        elif resp.status_code == 404:
            raise SourceSite404Error(url, resp.text)
        elif resp.status_code != 200:
            raise SourceSiteUnexpectedError(url, resp.status_code, resp.text)

        return resp

    def http_get(self, *args, **kwargs):
        return self._http_request("get", *args, **kwargs)

    def http_post(self, *args, **kwargs):
        return self._http_request("post", *args, **kwargs)
