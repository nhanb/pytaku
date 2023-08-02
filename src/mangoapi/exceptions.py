class SourceSiteResponseError(Exception):
    def __init__(self, url, status_code=None, response_text=None):
        self.url = url
        self.status_code = status_code
        self.response_text = response_text


class SourceSiteTimeoutError(SourceSiteResponseError):
    pass


class SourceSite5xxError(SourceSiteResponseError):
    pass


class SourceSite404Error(SourceSiteResponseError):
    def __init__(self, url, response_text):
        super().__init__(url, 404, response_text)


class SourceSiteUnexpectedError(SourceSiteResponseError):
    pass
