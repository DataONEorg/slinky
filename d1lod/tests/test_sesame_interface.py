import pytest
from urllib import quote_plus
import RDF

from d1lod.sesame import Store, Repository, Interface
from d1lod import dataone

def test_interface_can_be_created(interface):
    assert isinstance(interface, Interface)

def test_can_add_a_dataset(repo, interface):
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

def test_can_delete_then_add_a_datset_if_it_exists(repo, interface):
    repo.clear()

    identifier = 'doi:10.6073/AA/knb-lter-cdr.70061.123'
    doc = dataone.getSolrIndexFields(identifier)
    interface.addDataset(doc)
    interface.addDataset(doc)

    assert repo.size() == 42

def test_can_prepare_terms_correctly(interface):
    # RDF.Nodes
    assert isinstance(interface.prepareTerm(RDF.Node('asdf')), RDF.Node)

    # RDF.Uris
    assert isinstance(interface.prepareTerm(RDF.Uri('http://example.org')), RDF.Uri)

    # Strings
    assert isinstance(interface.prepareTerm('d1person:urn:uuid:6b1a2286-5205-47d8-9006-76ecce880c6a'), RDF.Uri)
    assert isinstance(interface.prepareTerm('test'), RDF.Node)
    assert isinstance(interface.prepareTerm('d1person:test'), RDF.Uri)

def test_add_a_person(repo, interface):
    repo.clear()

    interface.createModel()
    interface.addPerson({ 'last_name': 'Alpha' })
    interface.insertModel()
    assert repo.size() == 2

def test_can_reuse_a_person_uri(repo, interface):
    """Here we add a few datasets and assert an exepctation about how many
    unique glbase:Person statements we have.
    """
    repo.clear()

    assert repo.size() == 0

    interface.model = None
    interface.createModel()
    interface.addPerson({ 'last_name': 'Alpha', 'email': 'alpha@example.org'})
    interface.insertModel()

    assert repo.size() == 3

    interface.model = None
    interface.createModel()
    interface.addPerson({ 'last_name': 'Alpha', 'email': 'alpha@example.org'})
    interface.insertModel()
    interface.model = None

    assert repo.size() == 3


def test_can_reuse_an_org_uri(repo, interface):
    """Here we add a few datasets and assert an exepctation about how many
    unique glbase:Organization statements we have.
    """
    repo.clear()

    assert repo.size() == 0

    interface.model = None
    interface.createModel()
    interface.addOrganization({ 'name': 'Test Organization' })
    interface.insertModel()

    assert repo.size() == 2

    interface.model = None
    interface.createModel()
    interface.addOrganization({ 'name': 'Test Organization' })
    interface.insertModel()
    interface.model = None

    assert repo.size() == 2


def test_can_match_a_person_by_revision_chain(repo, interface):
    """This test relates to the matching rule which can match people down
    the revision chain of the document.
    """

    repo.clear()
    assert repo.size() == 0

    identifier = 'doi:10.6073/AA/knb-lter-luq.136.2'
    doc = dataone.getSolrIndexFields(identifier)
    interface.addDataset(doc)

    identifier = 'doi:10.6073/AA/knb-lter-luq.136.3'
    doc = dataone.getSolrIndexFields(identifier)
    interface.addDataset(doc)

    search = interface.find(p='rdf:type', o='glbase:Person')

    assert len(search) == 1


def test_deletes_the_right_triples_when_adding_an_existing_dataset(repo, interface):
    repo.clear()
    assert repo.size() == 0

    identifier = 'doi:10.6073/AA/knb-lter-luq.136.3'
    doc = dataone.getSolrIndexFields(identifier)
    interface.addDataset(doc)
    dataset = 'd1dataset:' + quote_plus(identifier)

    interface.deleteDataset(identifier)
    assert not interface.exists(s=dataset)
    assert not interface.exists(p='glbase:isCreatorOf')
    assert not interface.exists(p='glbase:hasIdentifier')

    # Check for size. We can do this here because I know what this dataset
    # should produce as an answer
    assert repo.size() == 6

def test_can_load_a_formats_list(interface):
    assert interface.formats is not None
    assert len(interface.formats) > 0

def test_can_use_the_formats_list(interface):
    identifier = 'doi:10.6073/AA/knb-lter-cdr.70061.123'
    doc = dataone.getSolrIndexFields(identifier)
    interface.addDataset(doc)

    assert interface.exists(o='<http://schema.geolink.org/dev/voc/dataone/format#003>')
