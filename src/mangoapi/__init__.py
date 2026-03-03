from .mangadex import Mangadex
from .weebcentral import Weebcentral
from .weebdex import Weebdex

"""
The mangoapi package is designed to be self-contained as if it was an external library.
Each Site object represents a user session on source site.
Instantiating and managing Site objects is the responsibility of the caller.
"""

SITES = {
    "mangadex": Mangadex,
    "weebcentral": Weebcentral,
    "weebdex": Weebdex,
}


def get_site_class(name):
    return SITES.get(name)
