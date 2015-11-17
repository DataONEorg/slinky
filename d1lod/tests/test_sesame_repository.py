import pytest

from d1lod import sesame

def test_repository_can_be_created(repo):
    assert isinstance(repo, sesame.Repository)

def test_repository_can_be_cleared(repo):
    repo.clear()
    repo.insert({'s':'owl:Thing', 'p':'rdf:type', 'o':'owl:OtherThing'})
    repo.clear()

    assert repo.size() == 0


def test_triples_can_be_added(repo):
    repo.clear()

    repo.insert({'s':'owl:Thing', 'p':'rdf:type', 'o':'owl:OtherThing'})
    assert repo.size() == 1

def test_repository_can_tell_us_its_size(repo):
    repo.clear()

    repo.insert({'s':'owl:A', 'p':'rdf:type', 'o':'owl:OtherThing'})
    repo.insert({'s':'owl:B', 'p':'rdf:type', 'o':'owl:OtherThing'})
    repo.insert({'s':'owl:C', 'p':'rdf:type', 'o':'owl:OtherThing'})

    assert repo.size() == 3

def test_repository_can_be_exported(repo):
    repo.clear()

    txt = repo.export()
    assert txt.startswith("@prefix")

def test_repository_can_list_its_statements(repo):
    repo.clear()

    txt = repo.export()
    assert txt.startswith("@prefix")

def test_repository_can_tell_us_its_namespaces(repo):
    repo.clear()

    ns = repo.namespaces()

    assert len(ns) > 0

def test_can_get_namespace(repo):
    assert repo.getNamespace('rdf') == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

def test_can_delete_namespace(repo):
    before = len(repo.namespaces())
    repo.removeNamespace('rdf')
    after = len(repo.namespaces())

    assert after == before - 1

def test_a_triple_can_be_found(repo):
    repo.insert({'s':'owl:A', 'p':'rdfs:label', 'o':"'Just an OWL A thing!'"})
    result = repo.find({'s':'?s', 'p':'?p', 'o':"'Just an OWL A thing!'"})

    assert len(result) == 1
    assert result[0]['s'] == '<http://www.w3.org/2002/07/owl#A>'
