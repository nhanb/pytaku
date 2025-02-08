from .mangadex import Mangadex
from .mangasee import Mangasee
from .weebcentral import Weebcentral

"""
The mangoapi package is designed to be self-contained as if it was an external library.
Each Site object represents a user session on source site.
Instantiating and managing Site objects is the responsibility of the caller.
"""

SITES = {
    "mangadex": Mangadex,
    "mangasee": Mangasee,
    "weebcentral": Weebcentral,
}


def get_site_class(name):
    return SITES.get(name)
