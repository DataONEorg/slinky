from urllib.parse import urlencode
from d1_client.cnclient_2_0 import CoordinatingNodeClient_2_0
import xml.etree.ElementTree as ET
from math import ceil
import logging

logger = logging.getLogger(__name__)

BASE_FILTER = {
    "q": "formatType:METADATA AND -obsoletedBy:*",
    "rows": "1000",
    "wt": "json",
}


class FilteredCoordinatingNodeClient(CoordinatingNodeClient_2_0):
    """
    Simple wrapper around CoordinatingNodeClient_2_0 to allow pre-defining query
    parameters so you don't have to specify them each time. This is useful for
    pointing at just a subset of all content.

    Example:

    client = FilteredCoordinatingNodeClient({
        'q':'datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People" AND formatType:METADATA AND -obsoletedBy:*',
        'rows': '100',
        'fl': 'identifier',
        'wt': 'json'
    })
    resp = client.query({'q':'title:foo'})

    """

    def __init__(self, q={}, **kwargs):
        logger.debug(f"Creating FilteredCoordinatingNodeClient with overrides {filter}")

        self.filter = BASE_FILTER
        self.filter = self.combine_filters(q)

        logger.debug(f"Final FilteredCoordinatingNodeClient filter is {self.filter}")

        super().__init__(**kwargs)

    def get_object(self, sysmeta):
        # TODO: Support non-XML based on sysmeta (mediaType?)
        response = super().get(sysmeta.identifier.value())

        return ET.fromstring(response.content)

    def get_system_metadata(self, identifier):
        return super().getSystemMetadata(identifier)

    def is_obsolete(self, identifier):
        sysmeta = self.getSystemMetadata(identifier)
        return sysmeta.obsoletedBy is not None

    def query(self, extra={}, filtered=True, engine="solr", auto_paginate=True):
        # Combine any extra filters with the defaults
        if filtered:
            params = self.combine_filters(extra)
        else:
            params = extra

        logger.debug("FilteredCoordinatingNodeClient.query: {}".format(params))

        response = super().query(engine, "?" + urlencode(params))

        # Determine if we need to paginate
        num_found = response["response"]["numFound"]
        docs = response["response"]["docs"]

        if not auto_paginate or num_found <= len(response["response"]["docs"]):
            return docs

        # Set up pagination params
        query_params = response["responseHeader"]["params"]

        if "rows" in query_params:
            rows = int(query_params["rows"])
        else:
            rows = 1000

        # Determine number of pages and get rest of pages after first
        pages_needed = ceil(num_found / rows)

        for i in range(1, pages_needed + 1):
            query_params["start"] = i * rows
            response = super().query(engine, "?" + urlencode(query_params))

            docs.extend(response["response"]["docs"])

        return docs

    def combine_filters(self, extra):
        """Combine the base filter parameters with extra parameters"""

        filter = self.filter.copy()

        # Process existing keys
        for key in filter:
            if key in extra:
                if key == "q":
                    filter[key] += " AND " + extra[key]
                else:
                    filter[key] = extra[key]

        # Add in non-existent keys
        for key in extra:
            if key in filter:
                continue

            filter[key] = extra[key]

        return filter

    def get_parts(self, identifier):
        ore_id = self.find_first_non_obsoleted_resource_map_for(identifier)

        if len(ore_id) == 0:
            return []

        # TODO: Handle pagingating. Probably handle that in query, not here
        docs = self.query(
            {"q": f'resourceMap:"{ore_id}"', "fl": "identifier", "wt": "json"},
            filtered=False,
        )

        ore_member_ids = [doc["identifier"] for doc in docs]

        return ore_member_ids

    def find_first_non_obsoleted_resource_map_for(self, identifier):
        docs = self.query(
            {
                "q": f'identifier:"{identifier}"',
                "fl": "identifier,resourceMap",
                "wt": "json",
            },
            filtered=False,
        )

        solr_doc = docs[0]

        # Return now if no resource maps exist for this identifier
        if "resourceMap" not in solr_doc:
            return []

        non_obsoleted_ids = [
            id for id in solr_doc["resourceMap"] if not self.is_obsolete(id)
        ]

        if len(non_obsoleted_ids) == 0:
            return []

        return non_obsoleted_ids[-1]
