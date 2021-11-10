from redis import Redis

from .stores.local_store import LocalStore
from .stores.virtuoso_store import VirtuosoStore

# A set of different environments that slinky can run under.
# When run through the CLI, a local (in memory) store is used without redis
# When run in development mode, the localhost redis is used
# When run in production, the redis host is behind the 'redis' service is used
ENVIRONMENTS = {
    "cli": {"store": LocalStore(), "redis": None},
    "development": {"store": VirtuosoStore(), "redis": Redis()},
    "production": {"store": VirtuosoStore(endpoint="http://virtuoso:8890"), "redis": Redis(host='redis')},
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
