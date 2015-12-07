import pytest
from urllib import quote_plus

from d1lod.sesame import Store, Repository, Interface
from d1lod import dataone

def test_interface_can_be_created(interface):
    assert isinstance(interface, Interface)
#
def test_can_add_a_dataset():
    """Test whether the right triples are added when we add a known dataset.
    This is essentially a regression test. The test doesn't verify all the
    triples the Interface should add are added but tests for a good number
    of them.

    The dataset being added is 'doi:10.6073/AA/knb-lter-cdr.70061.123' and it
    has related documents:

        - Solr: https://cn.dataone.org/cn/v1/query/solr/?q=id:*knb-lter-cdr.70061.123&rows=1&start=0
        - Meta: https://cn.dataone.org/cn/v1/meta/doi:10.6073/AA/knb-lter-cdr.70061.123
        - Object: https://cn.dataone.org/cn/v1/object/doi:10.6073/AA/knb-lter-cdr.70061.123
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
        'd1landing': 'https://search.dataone.org/#view/',
        "prov": "http://www.w3.org/ns/prov#"
    }

    store = Store('localhost', 8080)
    repo = Repository(store, 'test', ns = namespaces)
    interface = Interface(repo)

    repo.clear()

    identifier = 'doi:10.6073/AA/knb-lter-cdr.70061.123'
    doc = dataone.getSolrIndexFields(identifier)
    interface.addDataset(doc)

    assert interface.repository.size() == 38 # Tests for regression


    # Check for major classes. This dataset should produce...
    subject_dataset = 'd1dataset:' + quote_plus(identifier)

    assert interface.exists(subject_dataset, 'rdf:type', 'glbase:Dataset')
    assert interface.exists('?s', 'rdf:type', 'glbase:DigitalObject')
    assert interface.exists('?s', 'rdf:type', 'glbase:Person')
    assert interface.exists('?s', 'rdf:type', 'glbase:Identifier')


    # Dataset triples
    assert interface.exists(subject_dataset, 'rdf:type', 'glbase:Dataset')
    assert interface.exists(subject_dataset, 'rdfs:label', '?o')
    assert interface.exists(subject_dataset, 'glbase:description', '?o')
    assert interface.exists(subject_dataset, 'glbase:hasGeometryAsWktLiteral', '?o')
    assert interface.exists(subject_dataset, 'glbase:hasStartDate', '?o')
    assert interface.exists(subject_dataset, 'glbase:hasEndDate', '?o')
    assert interface.exists(subject_dataset, 'glbase:hasAuthoritativeDigitalRepository', '?o')
    assert interface.exists(subject_dataset, 'glbase:hasReplicaDigitalRepository', '?o')
    assert interface.exists(subject_dataset, 'glbase:hasOriginDigitalRepository', '?o')
    assert interface.exists(subject_dataset, 'prov:wasRevisionOf', '?o')
    assert interface.exists(subject_dataset, 'glbase:hasLandingPage', '?o')


    # Identifier (The subject will be some bnode)
    assert interface.exists('?s', 'glbase:hasIdentifier', '?o')
    assert interface.exists('?s', 'glbase:hasChecksum', '?o')
    assert interface.exists('?s', 'glbase:hasChecksumAlgorithm', '?o')
    assert interface.exists('?s', 'glbase:hasByteLength', '?o')
    assert interface.exists('?s', 'glbase:hasFormat', '?o')
    assert interface.exists('?s', 'glbase:dateUploaded', '?o')

    # Person
    assert interface.exists('?s', 'glbase:nameFull', '\'Mark Ritchie\'')
    assert interface.exists('?s', 'glbase:nameGiven', '\'Mark\'')
    assert interface.exists('?s', 'glbase:nameFamily', '\'Ritchie\'')
    assert interface.exists('?s', 'glbase:isCreatorOf', 'd1dataset:'+quote_plus('doi:10.6073/AA/knb-lter-cdr.70061.123'))

    # Negative assertions
    assert not interface.exists('?s', 'prov:wasRevisionOf', 'd1dataset:'+quote_plus('doi:10.6073/AA/knb-lter-cdr.70061.123'))
    assert not interface.exists('?s', 'glbase:nameFamily', '\'Ritchiee\'')
