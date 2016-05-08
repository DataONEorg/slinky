import pytest

from d1lod import sesame

@pytest.fixture(scope="module")
def store():
    return sesame.Store('localhost', 8080)

@pytest.fixture(scope="module")
def repo(store):
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

    repository = sesame.Repository(store, 'test', ns=namespaces)

    return repository

@pytest.fixture(scope="module")
def interface(repo):
    return sesame.Interface(repo)
