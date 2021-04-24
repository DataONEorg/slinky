from urllib.parse import urlencode
from d1_client.cnclient_2_0 import CoordinatingNodeClient_2_0
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(level=logging.DEBUG)

# TODO: Factor out
class UnsupportedPackageScenario(Exception):
    pass

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

    def __init__(self, filter={}, **kwargs):
        self.filter = filter
        super().__init__(**kwargs)


    def get_object(self, sysmeta):
        # TODO: Support non-XML based on sysmeta (mediaType?)
        response = super().get(sysmeta.identifier.value())

        return ET.fromstring(response.text)


    def get_system_metadata(self, identifier):
        return super().getSystemMetadata(identifier)


    def get_parts(self, identifier):
        package = self.query({
            'q': 'identifier:"{}"'.format(identifier),
            'fl': 'identifier,resourceMap',
            'wt': 'json'
        }, filtered=False)

        ore_id = None

        # TODO: Handle reality of OREs (ie multiple, non-obsoleted ores)
        try:
            ore_id = package['response']['docs'][0]['resourceMap'][0]
        except Exception:
            raise UnsupportedPackageScenario


        ore_member_ids = None

        # TODO: Handle pagingating. Probably handle that in query, not here
        ore_member_query = self.query({
            'q': 'resourceMap:"{}"'.format(ore_id),
            'fl': 'identifier',
            'wt': 'json'
        }, filtered=False)

        try:
            ore_member_ids = [doc['identifier'] for doc in ore_member_query['response']['docs']]
        except Exception:
            raise UnsupportedPackageScenario

        return ore_member_ids


    def query(self, extra={}, filtered=True, engine="solr"):
        if filtered:
            params = self.combine_filters(extra)
        else:
            params = extra

        logging.info("FilteredCoordinatingNodeClient.query: {}".format(params))

        return super().query(engine, "?" + urlencode(params))


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


if __name__ == "__main__":
    client = FilteredCoordinatingNodeClient({
        'q':'datasource:"urn:node:KNB" AND project:"State of Alaska\'s Salmon and People" AND formatType:METADATA AND -obsoletedBy:*',
        'rows': '1000',
        'fl': 'identifier',
        'wt': 'json'
    })
    resp = client.query({})
    print(resp)
    print(resp.url)
    print(resp.text)

