import os


# The Redis & Virtuoso parameters come from the environmental variables
# The default values are for the CLI. Note that the CLI
# doesn't use virtuoso, so the default value can stay as a service name
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
GRAPH_HOST = os.environ.get("GRAPH_HOST", "http://localhost")
GRAPH_PORT = os.environ.get("GRAPH_PORT", 8890)
BLAZEGRAPH_HOST = os.environ.get("BLAZEGRAPH_HOST", "http://localhost")
BLAZEGRAPH_PORT = os.environ.get("BLAZEGRAPH_PORT", 8080)


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
