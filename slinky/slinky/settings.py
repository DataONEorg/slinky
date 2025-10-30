import os

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
