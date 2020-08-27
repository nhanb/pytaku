class SourceSite5xxError(Exception):
    pass


class SourceSiteUnexpectedError(Exception):
    def __init__(self, status_code, resp_text):
        self.status_code = status_code
        self.resp_text = resp_text
