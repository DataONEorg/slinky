import pytest

from d1lod.sesame import Store, Repository, Interface
from d1lod import dataone

def test_interface_can_be_created(interface):
    assert isinstance(interface, Interface)


def test_can_add_a_dataset():
    """Test whether the right triples are added when we add a known dataset.

    We pass the store to this test because we'll need to specify namespaces.
    """
    namespaces = {
        'owl': 'http://www.w3.org/2002/07/owl#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'foaf': 'http://xmlns.com/foaf/0.1/',
        'dcterms': 'http://purl.org/dc/terms/',
        'datacite': 'http://purl.org/spar/datacite/',
        'glbase': 'http://schema.geolink.org/',
        'd1dataset': 'http://lod.dataone.org/dataset/',
        'd1person': 'http://lod.dataone.org/person/',
        'd1org': 'http://lod.dataone.org/organization/',
        'd1node': 'https://cn.dataone.org/cn/v1/node/',
        'd1landing': 'https://search.dataone.org/#view/'
    }

    store = Store('localhost', 8080)
    repo = Repository(store, 'test', ns = namespaces)
    interface = Interface(repo)


    repo.clear()

    identifier = 'doi:10.6073/AA/knb-lter-cdr.70061.123'
    doc = dataone.getSolrIndexFields(identifier)

    interface.addDataset(doc)

    assert interface.repository.size() == 20
