import pytest

from d1lod.sesame import Store, Repository, Interface
from d1lod import dataone

def test_interface_can_be_created(interface):
    assert isinstance(interface, Interface)

def test_can_add_a_dataset():
    """Test whether the right triples are added when we add a known dataset.

    We pass the store to this test because we'll need to specify namespaces.

    The dataset with PID: doi:10.6073/AA/knb-lter-cdr.70061.123

    has related information
    Solr: https://cn.dataone.org/cn/v1/query/solr/?q=id:*knb-lter-cdr.70061.123&rows=1&start=0
    Meta: https://cn.dataone.org/cn/v1/meta/doi:10.6073/AA/knb-lter-cdr.70061.123
    Object: https://cn.dataone.org/cn/v1/object/doi:10.6073/AA/knb-lter-cdr.70061.123

    Dataset:

    abstract: '...'
    title: '...''
    beginDate: '1989-01-01T00:00:00Z'
    endDate: '2003-01-01T00:00:00Z'
    originMN: urn:node:LTER
    replicaMNs:
        urn:node:CN
        urn:node:LTER
    authoritativeMN: urn:node:LTER

    dateUploaded: 2012-03-03T00:00:00Z

    eastBoundCoord: -93.16289
    southBoundCoord: 45.384865
    westBoundCoord: -93.22445
    northBoundCoord: 45.44138

    identifier;
        doi:10.6073/AA/knb-lter-cdr.70061.123
    obsoletes: doi:10.6073/AA/knb-lter-cdr.70061.122

    Digital Object 1: Metadata
    checksum: 4f3d47e4110c4bb7dd24d74bb81f005b
    checksumAlgo: MD5
    format: eml://ecoinformatics.org/eml-2.1.0
    formattype: METADATA
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
