import os


# The Redis & Virtuoso parameters come from the environmental variables
# The default values are for the CLI. Note that the CLI
# doesn't use virtuoso, so the default value can stay as a service name
REDIS_HOST = os.environ.get("REDIS_HOST", None)
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
VIRTUOSO_HOST = os.environ.get("VIRTUOSO_HOST", "http://virtuoso")
VIRTUOSO_PORT = os.environ.get("VIRTUOSO_PORT", 8890)

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
