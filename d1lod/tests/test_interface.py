import pytest
from urllib.parse import quote_plus
import RDF
import urllib.request, urllib.parse, urllib.error

from d1lod.interface import Interface
from d1lod import dataone

def test_interface_can_be_created(interface):
    assert isinstance(interface, Interface)


def test_can_delete_then_add_a_datset_if_it_exists(interface):
    interface.graph.clear()

    interface.model = None

    identifier = 'doi:10.5063/F1125QWP'
    interface.addDataset(identifier)

    assert interface.graph.size() == 15  # Test for regression


def test_can_prepare_terms_correctly(interface):
    # RDF.Nodes
    assert isinstance(interface.prepareTerm(RDF.Node('asdf')), RDF.Node)

    # RDF.Uris
    assert isinstance(interface.prepareTerm(RDF.Uri('http://example.org')), RDF.Uri)

    # Strings
    assert isinstance(interface.prepareTerm('d1person:urn:uuid:6b1a2286-5205-47d8-9006-76ecce880c6a'), RDF.Uri)
    assert isinstance(interface.prepareTerm('test'), RDF.Node)
    assert isinstance(interface.prepareTerm('d1person:test'), RDF.Uri)


def test_add_a_person(interface):
    interface.graph.clear()

    interface.createModel()
    interface.addPerson({ 'last_name': 'Alpha' })
    interface.insertModel()
    interface.model = None
    assert interface.graph.size() == 2


def test_can_reuse_a_person_uri(interface):
    """Here we add a few datasets and assert an exepctation about how many
    unique schema:Person statements we have.
    """
    interface.graph.clear()

    assert interface.graph.size() == 0

    interface.model = None
    interface.createModel()
    interface.addPerson({ 'last_name': 'Alpha', 'email': 'alpha@example.org'})
    interface.insertModel()

    assert interface.graph.size() == 3

    interface.model = None
    interface.createModel()
    interface.addPerson({ 'last_name': 'Alpha', 'email': 'alpha@example.org'})
    interface.insertModel()
    interface.model = None

    assert interface.graph.size() == 3


def test_can_reuse_an_org_uri(interface):
    """Here we add a few datasets and assert an exepctation about how many
    unique schema:Organization statements we have.
    """
    interface.graph.clear()

    assert interface.graph.size() == 0

    interface.model = None
    interface.createModel()
    interface.addOrganization({ 'name': 'Test Organization' })
    interface.insertModel()

    assert interface.graph.size() == 2

    interface.model = None
    interface.createModel()
    interface.addOrganization({ 'name': 'Test Organization' })
    interface.insertModel()
    interface.model = None

    assert interface.graph.size() == 2


# def test_can_prepare_terms_properly(interface):
#     assert isinstance(interface.prepareTerm('test'), RDF.Node)
#     assert isinstance(interface.prepareTerm('d1dataset:' + 'test'), RDF.Uri)

#     # Invalid (missing :)
#     assert isinstance(interface.prepareTerm('d1dataset' + 'test'), RDF.Node)

#     assert isinstance(interface.prepareTerm('http://test.com/'), RDF.Uri)
#     assert isinstance(interface.prepareTerm('?p'), str)
#     assert isinstance(interface.prepareTerm('test'), RDF.Node)


def test_can_load_a_formats_list(interface):
    assert interface.formats is not None
    assert len(interface.formats) > 0
