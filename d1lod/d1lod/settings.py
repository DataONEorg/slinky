from redis import Redis

from .stores.local_store import LocalStore
from .stores.virtuoso_store import VirtuosoStore

ENVIRONMENTS = {
    "cli": {"store": LocalStore(), "redis": None},
    "development": {"store": VirtuosoStore(), "redis": Redis()},
    "production": {"store": VirtuosoStore(), "redis": Redis()},
}

FILTERS = {
    "default": {},
    "sasap": {
        "q": 'datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People"',
    },
    "arctica": {
        "q": 'datasource:"urn:node:ARCTIC"',
    },
    "dataone": {},
}
