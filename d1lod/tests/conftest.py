import pytest

from d1lod.d1lod.graph import Graph
from d1lod.d1lod.interface import Interface

@pytest.fixture(scope="module")
def store():
    return Graph('localhost', 8890, 'test')

@pytest.fixture(scope="module")
def graph(store):
    namespaces = {
        'owl': 'http://www.w3.org/2002/07/owl#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'foaf': 'http://xmlns.com/foaf/0.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'datacite': 'http://purl.org/spar/datacite/',
        'geolink': 'http://schema.geolink.org/1.0/base/main#',
        'd1dataset': 'http://lod.dataone.org/dataset/',
        'd1person': 'http://lod.dataone.org/person/',
        'd1org': 'http://lod.dataone.org/organization/',
        'd1node': 'https://cn.dataone.org/cn/v1/node/',
        'd1landing': 'https://search.dataone.org/#view/',
        "prov": "http://www.w3.org/ns/prov#"
    }

    graphh = Graph('localhost', 8890, 'test', ns=namespaces)

    return graphh

@pytest.fixture(scope="module")
def interface(graph):
    return Interface(graph)
