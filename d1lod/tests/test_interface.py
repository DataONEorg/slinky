import pytest
from urllib import quote_plus
import RDF

from d1lod.d1lod.graph import Graph
from d1lod.d1lod.interface import Interface
from d1lod.d1lod import dataone

def test_interface_can_be_created(interface):
    assert isinstance(interface, Interface)


def test_can_add_a_dataset(graph, interface):
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

    graph.clear()

    identifier = 'doi:10.5063/F1MK6B5J'

    interface.model = None
    interface.addDataset(identifier)

    assert interface.graph.size() == 40  # Tests for regression

    # Check for major classes. This dataset should produce...
    subject_dataset = 'd1dataset:' + quote_plus(identifier)

    assert interface.exists(subject_dataset, 'rdf:type', 'geolink:Dataset')
    assert interface.exists('?s', 'rdf:type', 'geolink:DigitalObject')
    assert interface.exists('?s', 'rdf:type', 'geolink:Person')
    assert interface.exists('?s', 'rdf:type', 'geolink:Identifier')

    # Dataset triples
    assert interface.exists(subject_dataset, 'rdf:type', 'geolink:Dataset')
    assert interface.exists(subject_dataset, 'rdfs:label', '?o')
    assert interface.exists(subject_dataset, 'geolink:description', '?o')
    assert interface.exists(subject_dataset, 'geolink:hasGeometryAsWktLiteral', '?o')
    assert interface.exists(subject_dataset, 'geolink:hasStartDate', '?o')
    assert interface.exists(subject_dataset, 'geolink:hasEndDate', '?o')
    assert interface.exists(subject_dataset, 'prov:wasRevisionOf', '?o')
    assert interface.exists(subject_dataset, 'geolink:hasLandingPage', '?o')

    # Identifier (The subject will be some bnode)
    assert interface.exists('?s', 'geolink:hasIdentifier', '?o')
    assert interface.exists('?s', 'geolink:hasChecksum', '?o')
    assert interface.exists('?s', 'geolink:hasChecksumAlgorithm', '?o')
    assert interface.exists('?s', 'geolink:hasByteLength', '?o')
    assert interface.exists('?s', 'geolink:hasFormat', '?o')
    assert interface.exists('?s', 'geolink:dateUploaded', '?o')

    # Person
    assert interface.exists('?s', 'geolink:nameFull', '\'Mark Ritchie\'')
    assert interface.exists('?s', 'geolink:nameGiven', '\'Mark\'')
    assert interface.exists('?s', 'geolink:nameFamily', '\'Ritchie\'')
    assert interface.exists('?s', 'geolink:isCreatorOf', 'd1dataset:'+quote_plus('doi:10.6073/AA/knb-lter-cdr.70061.123'))

    # Negative assertions
    assert not interface.exists('?s', 'prov:wasRevisionOf', 'd1dataset:'+quote_plus('doi:10.6073/AA/knb-lter-cdr.70061.123'))
    assert not interface.exists('?s', 'geolink:nameFamily', '\'Ritchiee\'')


def test_can_delete_then_add_a_datset_if_it_exists(graph, interface):
    graph.clear()

    interface.model = None

    identifier = 'doi:10.5063/F1MK6B5J'
    interface.addDataset(identifier)
    interface.addDataset(identifier)

    assert graph.size() == 44  # Test for regression


def test_can_prepare_terms_correctly(interface):
    # RDF.Nodes
    assert isinstance(interface.prepareTerm(RDF.Node('asdf')), RDF.Node)

    # RDF.Uris
    assert isinstance(interface.prepareTerm(RDF.Uri('http://example.org')), RDF.Uri)

    # Strings
    assert isinstance(interface.prepareTerm('d1person:urn:uuid:6b1a2286-5205-47d8-9006-76ecce880c6a'), RDF.Uri)
    assert isinstance(interface.prepareTerm('test'), RDF.Node)
    assert isinstance(interface.prepareTerm('d1person:test'), RDF.Uri)


def test_add_a_person(graph, interface):
    graph.clear()

    interface.createModel()
    interface.addPerson({ 'last_name': 'Alpha' })
    interface.insertModel()
    interface.model = None
    assert graph.size() == 2


def test_can_reuse_a_person_uri(graph, interface):
    """Here we add a few datasets and assert an exepctation about how many
    unique geolink:Person statements we have.
    """
    graph.clear()

    assert graph.size() == 0

    interface.model = None
    interface.createModel()
    interface.addPerson({ 'last_name': 'Alpha', 'email': 'alpha@example.org'})
    interface.insertModel()

    assert graph.size() == 3

    interface.model = None
    interface.createModel()
    interface.addPerson({ 'last_name': 'Alpha', 'email': 'alpha@example.org'})
    interface.insertModel()
    interface.model = None

    assert graph.size() == 3


def test_can_reuse_an_org_uri(graph, interface):
    """Here we add a few datasets and assert an exepctation about how many
    unique geolink:Organization statements we have.
    """
    graph.clear()

    assert graph.size() == 0

    interface.model = None
    interface.createModel()
    interface.addOrganization({ 'name': 'Test Organization' })
    interface.insertModel()

    assert graph.size() == 2

    interface.model = None
    interface.createModel()
    interface.addOrganization({ 'name': 'Test Organization' })
    interface.insertModel()
    interface.model = None

    assert graph.size() == 2


def test_can_match_a_person_by_revision_chain(graph, interface):
    """This test relates to the matching rule which can match people down
    the revision chain of the document.
    """

    graph.clear()
    assert graph.size() == 0
    interface.model = None
    identifier = 'doi:10.5063/F1MK6B5J'

    interface.addDataset(identifier)

    identifier = 'doi:10.5063/F1MK6B5J'

    interface.model = None
    interface.addDataset(identifier)

    search = interface.find(p='rdf:type', o='geolink:Person')

    assert len(search) == 1


def test_deletes_the_right_triples_when_adding_an_existing_dataset(graph, interface):
    graph.clear()
    assert graph.size() == 0

    identifier = 'doi:10.5063/F1MK6B5J'

    interface.model = None
    interface.addDataset(identifier)
    dataset = 'd1dataset:' + quote_plus(identifier)

    interface.deleteDataset(identifier)
    assert not interface.exists(s=dataset)
    assert not interface.exists(p='geolink:isCreatorOf')
    assert not interface.exists(p='geolink:hasIdentifier')

    # Check for size. We can do this here because I know what this dataset
    # should produce as an answer
    assert graph.size() == 6


def test_can_prepare_terms_properly(interface):
    assert isinstance(interface.prepareTerm('test'), RDF.Node)
    assert isinstance(interface.prepareTerm('d1dataset:' + 'test'), RDF.Uri)

    # Invalid (missing :)
    assert isinstance(interface.prepareTerm('d1dataset' + 'test'), RDF.Node)

    assert isinstance(interface.prepareTerm('http://test.com/'), RDF.Uri)
    assert isinstance(interface.prepareTerm('?p'), str)
    assert isinstance(interface.prepareTerm('test'), RDF.Node)


def test_can_load_a_formats_list(interface):
    assert interface.formats is not None
    assert len(interface.formats) > 0


def test_can_use_the_formats_list(interface):
    identifier = 'doi:10.5063/F1MK6B5J'

    interface.model = None
    interface.addDataset(identifier)

    assert interface.exists(o='<http://schema.geolink.org/dev/voc/dataone/format#003>')

