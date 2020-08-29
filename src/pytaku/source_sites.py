import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from mangoapi import get_site_class

from .conf import config
from .persistence import KeyvalStore

"""
This module adapts mangoapi's API to a more convenient one for app-wide use.
States are all handled here, exposing only a functional API to the rest of the app.
"""

_site_objs = {}


def _get_site(name):
    global _site_objs
    site = _site_objs.get(name)
    if not site:
        site_class = get_site_class(name)
        assert site_class is not None
        site = site_class()
        if name == "mangadex":
            site.username = config.MANGADEX_USERNAME
            site.password = config.MANGADEX_PASSWORD
        elif name == "mangasee":
            site.keyval_store = KeyvalStore
    return site


def get_chapter(site_name, title_id, chapter_id):
    return _get_site(site_name).get_chapter(title_id, chapter_id)


def get_title(site_name, title_id):
    return _get_site(site_name).get_title(title_id)


def search_title(site_name, query):
    return _get_site(site_name).search_title(query)


def title_cover(site_name, title_id, cover_ext):
    return _get_site(site_name).title_cover(title_id, cover_ext)


def title_thumbnail(site_name, title_id):
    return _get_site(site_name).title_thumbnail(title_id)


def title_source_url(site_name, title_id):
    return _get_site(site_name).title_source_url(title_id)


def search_title_all_sites(query):
    """
    Returns dict in the form of {site_name: List[Title]}
    I should really look into proper type annotations huh.
    """
    site_names = ("mangasee", "mangadex")
    results = {}

    def safe_search(site_name, query):
        try:
            return search_title(site_name, query)
        except Exception:
            print(f"{site_name}'s search function shat the bed:")
            traceback.print_exc()
            return []

    # Concurrently search from multiple sites.
    # Obviously network I/O bound so a thread pool is appropriate enough.
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_site_name = {
            executor.submit(safe_search, site_name, query): site_name
            for site_name in site_names
        }
        for future in as_completed(future_to_site_name):
            site_results = future.result()
            site_name = future_to_site_name[future]
            results[site_name] = site_results

    return results
