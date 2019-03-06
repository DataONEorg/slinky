import pytest
from urllib import quote_plus
import RDF
import urllib

from d1lod.graph import Graph
from d1lod.interface import Interface
from d1lod import dataone

def test_interface_can_be_created(interface):
    assert isinstance(interface, Interface)


def test_can_delete_then_add_a_datset_if_it_exists(graph, interface):
    graph.clear()

    interface.model = None

    identifier = 'doi:10.5063/F1125QWP'
    interface.addDataset(identifier)

    print(graph.size())
    # assert graph.size() == 44  # Test for regression


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
    identifier = 'doi:10.5063/F1125QWP'

    interface.model = None
    interface.addDataset(identifier)

    assert interface.exists(o='<http://schema.geolink.org/dev/voc/dataone/format#004>')

