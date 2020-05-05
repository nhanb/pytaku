from importlib import import_module
from urllib.parse import urlparse

available_sites = {"mangadex.org": ".mangadex"}


# return suitable module from url
def get_site(url):
    netloc = urlparse(url).netloc
    module_name = available_sites.get(netloc)
    return (
        None
        if module_name is None
        else import_module(module_name, "pytaku_web.scraper")
    )
